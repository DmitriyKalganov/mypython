#!/usr/bin/env python3
"""
Full migration script for BigQuery to Apache Unomi.
This script performs the initial bulk migration of all data.
"""
import sys
import time
from datetime import datetime
from tqdm import tqdm

from config import Config
from bigquery_extractor import BigQueryExtractor
from unomi_loader import UnomiLoader
from checkpoint_manager import CheckpointManager, MigrationStats
from utils import (
    setup_logging,
    transform_bigquery_to_unomi_event,
    calculate_eta,
    format_number,
    RateLimiter,
    validate_row
)


class FullMigration:
    """Orchestrates the full data migration process."""

    def __init__(self):
        """Initialize migration components."""
        # Validate configuration
        Config.validate()
        Config.display()

        # Setup logging
        self.logger = setup_logging(Config.LOG_DIR, Config.LOG_LEVEL)
        self.logger.info("="*60)
        self.logger.info("FULL MIGRATION STARTED")
        self.logger.info("="*60)

        # Initialize components
        self.extractor = BigQueryExtractor(
            project_id=Config.BIGQUERY_PROJECT_ID,
            dataset=Config.BIGQUERY_DATASET,
            table=Config.BIGQUERY_TABLE,
            credentials_path=Config.BIGQUERY_CREDENTIALS_PATH
        )

        self.loader = UnomiLoader(
            api_url=Config.UNOMI_API_URL,
            username=Config.UNOMI_API_USERNAME,
            password=Config.UNOMI_API_PASSWORD,
            scope=Config.UNOMI_SCOPE,
            max_retries=Config.MAX_RETRIES,
            retry_wait_multiplier=Config.RETRY_WAIT_EXPONENTIAL_MULTIPLIER,
            retry_wait_min=Config.RETRY_WAIT_MIN_SECONDS,
            retry_wait_max=Config.RETRY_WAIT_MAX_SECONDS
        )

        self.checkpoint_manager = CheckpointManager(
            checkpoint_dir=Config.CHECKPOINT_DIR,
            migration_name='full_migration'
        )

        self.stats = MigrationStats(Config.CHECKPOINT_DIR)
        self.rate_limiter = RateLimiter(Config.RATE_LIMIT_REQUESTS_PER_SECOND)

    def verify_setup(self) -> bool:
        """
        Verify that all systems are ready for migration.

        Returns:
            True if setup is valid, False otherwise
        """
        self.logger.info("Verifying setup...")

        # Check BigQuery connection and schema
        self.logger.info("Checking BigQuery connection...")
        if not self.extractor.validate_table_schema():
            self.logger.error("BigQuery table schema validation failed")
            return False

        table_info = self.extractor.get_table_info()
        self.logger.info(f"BigQuery table rows: {format_number(table_info['num_rows'])}")
        self.logger.info(f"BigQuery table size: {table_info['num_bytes']:,} bytes")

        # Check Unomi connection
        self.logger.info("Checking Unomi API connection...")
        if not self.loader.test_connection():
            self.logger.error("Unomi API connection failed")
            return False

        self.logger.info("Setup verification completed successfully")
        return True

    def run(self, resume: bool = True):
        """
        Run the full migration.

        Args:
            resume: If True, resume from last checkpoint if available
        """
        start_time = datetime.now()
        self.stats.update(start_time=start_time.isoformat())

        try:
            # Verify setup
            if not self.verify_setup():
                self.logger.error("Setup verification failed. Aborting migration.")
                return

            # Get total rows
            total_rows = self.extractor.get_total_rows()
            self.stats.update(total_records=total_rows)

            # Check for existing checkpoint
            start_offset = 0
            if resume and self.checkpoint_manager.checkpoint_exists():
                checkpoint = self.checkpoint_manager.load_checkpoint()
                if checkpoint:
                    start_offset = checkpoint.get('offset', 0)
                    self.logger.info(
                        f"Resuming from checkpoint: offset={format_number(start_offset)}"
                    )
            else:
                self.logger.info("Starting fresh migration (no checkpoint)")

            # Process batches
            batch_number = start_offset // Config.BATCH_SIZE
            processed_rows = start_offset

            self.logger.info(
                f"Processing {format_number(total_rows)} rows "
                f"in batches of {format_number(Config.BATCH_SIZE)}"
            )

            # Progress bar
            pbar = tqdm(
                total=total_rows,
                initial=start_offset,
                desc="Migration Progress",
                unit="rows",
                unit_scale=True
            )

            migration_start = time.time()

            # Extract and load batches
            for batch in self.extractor.extract_all_batches(
                batch_size=Config.BATCH_SIZE,
                start_offset=start_offset
            ):
                batch_number += 1
                batch_start = time.time()

                # Validate and transform rows
                valid_rows = []
                invalid_count = 0

                for row in batch:
                    if validate_row(row):
                        event = transform_bigquery_to_unomi_event(row, Config.UNOMI_SCOPE)
                        valid_rows.append(event)
                    else:
                        invalid_count += 1
                        self.logger.warning(f"Invalid row skipped: {row.get('id', 'unknown')}")

                if invalid_count > 0:
                    self.stats.update(failed_records=self.stats.stats['failed_records'] + invalid_count)

                # Load batch to Unomi
                successful, failed, failed_events = self.loader.load_batch(valid_rows)

                # Apply rate limiting
                for _ in range(len(valid_rows)):
                    self.rate_limiter.wait()

                # Update statistics
                processed_rows += len(batch)
                self.stats.increment('processed_records', len(batch))
                self.stats.increment('successful_records', successful)
                self.stats.increment('failed_records', failed)
                self.stats.increment('batches_processed', 1)

                # Save failed events if any
                if failed_events:
                    failed_file = self.checkpoint_manager.save_failed_records(
                        failed_events,
                        {
                            'batch_number': batch_number,
                            'offset': processed_rows - len(batch)
                        }
                    )
                    self.logger.warning(
                        f"Saved {len(failed_events)} failed events to {failed_file}"
                    )

                # Update progress bar
                pbar.update(len(batch))

                batch_time = time.time() - batch_start
                elapsed = time.time() - migration_start
                eta = calculate_eta(processed_rows - start_offset, total_rows - start_offset, elapsed)

                pbar.set_postfix({
                    'batch': batch_number,
                    'success': successful,
                    'failed': failed,
                    'rate': f"{len(batch)/batch_time:.1f} rows/s",
                    'ETA': eta
                })

                # Save checkpoint
                if batch_number % Config.CHECKPOINT_INTERVAL == 0:
                    self.checkpoint_manager.save_checkpoint({
                        'offset': processed_rows,
                        'batch_number': batch_number,
                        'total_rows': total_rows,
                        'successful': self.stats.stats['successful_records'],
                        'failed': self.stats.stats['failed_records']
                    })
                    self.logger.info(f"Checkpoint saved at offset {format_number(processed_rows)}")

            pbar.close()

            # Migration completed
            end_time = datetime.now()
            self.stats.update(end_time=end_time.isoformat())

            self.logger.info("="*60)
            self.logger.info("MIGRATION COMPLETED SUCCESSFULLY")
            self.logger.info("="*60)

            # Print final statistics
            self.stats.print_summary()

            # Clean up checkpoint
            self.checkpoint_manager.delete_checkpoint()
            self.logger.info("Checkpoint file removed")

        except KeyboardInterrupt:
            self.logger.warning("\nMigration interrupted by user")
            self.logger.info(
                f"Progress saved. Processed {format_number(processed_rows)} rows. "
                "Run again with resume=True to continue."
            )

        except Exception as e:
            self.logger.error(f"Migration failed with error: {e}", exc_info=True)
            self.stats.add_error(str(e), batch_number)

        finally:
            # Clean up
            self.loader.close()
            self.logger.info("Migration process ended")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Full migration from BigQuery to Apache Unomi'
    )
    parser.add_argument(
        '--no-resume',
        action='store_true',
        help='Start fresh migration (ignore existing checkpoint)'
    )

    args = parser.parse_args()

    migration = FullMigration()
    migration.run(resume=not args.no_resume)


if __name__ == '__main__':
    main()
