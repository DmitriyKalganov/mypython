#!/usr/bin/env python3
"""
Incremental sync script for BigQuery to Apache Unomi.
This script syncs only new records based on a watermark.
"""
import sys
import time
from datetime import datetime

from config import Config
from bigquery_extractor import BigQueryExtractor
from unomi_loader import UnomiLoader
from checkpoint_manager import WatermarkManager, MigrationStats
from utils import (
    setup_logging,
    transform_bigquery_to_unomi_event,
    format_number,
    RateLimiter,
    validate_row
)


class IncrementalSync:
    """Orchestrates incremental data synchronization."""

    def __init__(self):
        """Initialize sync components."""
        # Validate configuration
        Config.validate()

        # Setup logging
        self.logger = setup_logging(Config.LOG_DIR, Config.LOG_LEVEL)
        self.logger.info("="*60)
        self.logger.info("INCREMENTAL SYNC STARTED")
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

        self.watermark_manager = WatermarkManager(Config.WATERMARK_FILE)
        self.stats = MigrationStats(Config.CHECKPOINT_DIR)
        self.rate_limiter = RateLimiter(Config.RATE_LIMIT_REQUESTS_PER_SECOND)

    def get_last_watermark(self):
        """
        Get the last watermark value.

        Returns:
            Last watermark value, or None if not exists
        """
        watermark = self.watermark_manager.load_watermark()

        if watermark:
            self.logger.info(
                f"Last watermark: {watermark['value']} "
                f"(column: {watermark['column']}, "
                f"saved at: {watermark['timestamp']})"
            )
            return watermark['value']
        else:
            self.logger.warning("No watermark found. This might be the first sync.")
            # Get the max value from BigQuery as starting point
            max_value = self.extractor.get_max_value(Config.SYNC_COLUMN)
            self.logger.info(f"Using current max value as watermark: {max_value}")
            return max_value

    def run(self):
        """Run the incremental sync."""
        start_time = datetime.now()
        self.logger.info(f"Sync started at {start_time.isoformat()}")

        try:
            # Test connections
            self.logger.info("Testing connections...")

            if not self.loader.test_connection():
                self.logger.error("Unomi API connection failed")
                return

            # Get last watermark
            last_watermark = self.get_last_watermark()

            if not last_watermark:
                self.logger.error(
                    "Cannot proceed without a watermark. "
                    "Please run full migration first or set watermark manually."
                )
                return

            # Extract incremental data
            self.logger.info(
                f"Extracting records where {Config.SYNC_COLUMN} > {last_watermark}"
            )

            total_processed = 0
            total_successful = 0
            total_failed = 0
            batch_count = 0
            new_watermark = last_watermark

            # Process batches
            for batch in self.extractor.extract_incremental(
                watermark_column=Config.SYNC_COLUMN,
                watermark_value=last_watermark,
                batch_size=Config.BATCH_SIZE
            ):
                if not batch:
                    break

                batch_count += 1
                self.logger.info(f"Processing batch {batch_count} ({len(batch)} records)")

                # Validate and transform rows
                valid_rows = []
                invalid_count = 0

                for row in batch:
                    if validate_row(row):
                        event = transform_bigquery_to_unomi_event(row, Config.UNOMI_SCOPE)
                        valid_rows.append(event)

                        # Track the highest watermark value in this batch
                        row_watermark = row.get(Config.SYNC_COLUMN)
                        if row_watermark:
                            if isinstance(row_watermark, datetime):
                                row_watermark = row_watermark.isoformat()
                            else:
                                row_watermark = str(row_watermark)

                            if row_watermark > str(new_watermark):
                                new_watermark = row_watermark
                    else:
                        invalid_count += 1
                        self.logger.warning(
                            f"Invalid row skipped: {row.get('id', 'unknown')}"
                        )

                # Load batch to Unomi
                if valid_rows:
                    successful, failed, failed_events = self.loader.load_batch(valid_rows)

                    # Apply rate limiting
                    for _ in range(len(valid_rows)):
                        self.rate_limiter.wait()

                    total_processed += len(batch)
                    total_successful += successful
                    total_failed += failed + invalid_count

                    self.logger.info(
                        f"Batch {batch_count}: {successful} successful, "
                        f"{failed} failed, {invalid_count} invalid"
                    )

                    # Log failed events
                    if failed_events:
                        for failed_event in failed_events:
                            self.logger.error(
                                f"Failed event: {failed_event['event'].get('source', {}).get('itemId')} "
                                f"- {failed_event['error']}"
                            )

            # Update statistics
            if total_processed > 0:
                self.logger.info("="*60)
                self.logger.info("SYNC SUMMARY")
                self.logger.info("="*60)
                self.logger.info(f"Total Records:    {format_number(total_processed)}")
                self.logger.info(f"Successful:       {format_number(total_successful)}")
                self.logger.info(f"Failed:           {format_number(total_failed)}")
                self.logger.info(f"Batches:          {batch_count}")
                self.logger.info(f"Old Watermark:    {last_watermark}")
                self.logger.info(f"New Watermark:    {new_watermark}")
                self.logger.info("="*60)

                # Save new watermark
                self.watermark_manager.save_watermark(
                    new_watermark,
                    Config.SYNC_COLUMN
                )
                self.logger.info(f"Watermark updated to: {new_watermark}")

            else:
                self.logger.info("No new records to sync")

            end_time = datetime.now()
            duration = end_time - start_time
            self.logger.info(f"Sync completed in {duration}")

        except KeyboardInterrupt:
            self.logger.warning("\nSync interrupted by user")

        except Exception as e:
            self.logger.error(f"Sync failed with error: {e}", exc_info=True)

        finally:
            # Clean up
            self.loader.close()
            self.logger.info("Sync process ended")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Incremental sync from BigQuery to Apache Unomi'
    )
    parser.add_argument(
        '--reset-watermark',
        action='store_true',
        help='Reset watermark to current max value'
    )

    args = parser.parse_args()

    sync = IncrementalSync()

    if args.reset_watermark:
        logger = setup_logging(Config.LOG_DIR, Config.LOG_LEVEL)
        logger.info("Resetting watermark to current max value...")

        max_value = sync.extractor.get_max_value(Config.SYNC_COLUMN)
        sync.watermark_manager.save_watermark(max_value, Config.SYNC_COLUMN)

        logger.info(f"Watermark reset to: {max_value}")
        return

    sync.run()


if __name__ == '__main__':
    main()
