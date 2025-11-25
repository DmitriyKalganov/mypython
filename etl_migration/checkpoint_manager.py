"""
Checkpoint manager for tracking migration progress and enabling recovery.
"""
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any


class CheckpointManager:
    """Manages checkpoints for migration progress tracking."""

    def __init__(self, checkpoint_dir: str, migration_name: str = 'full_migration'):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_dir: Directory to store checkpoint files
            migration_name: Name of the migration (used for checkpoint filename)
        """
        self.checkpoint_dir = checkpoint_dir
        self.migration_name = migration_name
        self.checkpoint_file = os.path.join(
            checkpoint_dir,
            f'{migration_name}_checkpoint.json'
        )

        os.makedirs(checkpoint_dir, exist_ok=True)

    def save_checkpoint(self, data: Dict[str, Any]) -> None:
        """
        Save checkpoint data to file.

        Args:
            data: Dictionary containing checkpoint data
        """
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'migration_name': self.migration_name,
            **data
        }

        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)

    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint data from file.

        Returns:
            Dictionary containing checkpoint data, or None if no checkpoint exists
        """
        if not os.path.exists(self.checkpoint_file):
            return None

        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load checkpoint: {e}")
            return None

    def checkpoint_exists(self) -> bool:
        """
        Check if a checkpoint exists.

        Returns:
            True if checkpoint exists, False otherwise
        """
        return os.path.exists(self.checkpoint_file)

    def delete_checkpoint(self) -> None:
        """Delete the checkpoint file."""
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)

    def save_failed_records(self, records: list, error_info: Dict[str, Any]) -> str:
        """
        Save failed records to a separate file for manual review.

        Args:
            records: List of records that failed to process
            error_info: Dictionary containing error information

        Returns:
            Path to the failed records file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        failed_file = os.path.join(
            self.checkpoint_dir,
            f'failed_records_{timestamp}.json'
        )

        data = {
            'timestamp': datetime.now().isoformat(),
            'error_info': error_info,
            'records': records
        }

        with open(failed_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return failed_file


class WatermarkManager:
    """Manages watermark for incremental synchronization."""

    def __init__(self, watermark_file: str):
        """
        Initialize watermark manager.

        Args:
            watermark_file: Path to watermark file
        """
        self.watermark_file = watermark_file
        os.makedirs(os.path.dirname(watermark_file), exist_ok=True)

    def save_watermark(self, watermark_value: Any, column_name: str = 'date_ev') -> None:
        """
        Save watermark value.

        Args:
            watermark_value: Value to save as watermark
            column_name: Name of the column used for watermarking
        """
        watermark_data = {
            'column': column_name,
            'value': str(watermark_value),
            'timestamp': datetime.now().isoformat()
        }

        with open(self.watermark_file, 'w', encoding='utf-8') as f:
            json.dump(watermark_data, f, indent=2, ensure_ascii=False)

    def load_watermark(self) -> Optional[Dict[str, Any]]:
        """
        Load watermark value.

        Returns:
            Dictionary containing watermark data, or None if no watermark exists
        """
        if not os.path.exists(self.watermark_file):
            return None

        try:
            with open(self.watermark_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load watermark: {e}")
            return None

    def get_watermark_value(self) -> Optional[str]:
        """
        Get the watermark value only.

        Returns:
            Watermark value as string, or None if no watermark exists
        """
        watermark = self.load_watermark()
        return watermark['value'] if watermark else None

    def delete_watermark(self) -> None:
        """Delete the watermark file."""
        if os.path.exists(self.watermark_file):
            os.remove(self.watermark_file)


class MigrationStats:
    """Track and persist migration statistics."""

    def __init__(self, checkpoint_dir: str):
        """
        Initialize migration stats tracker.

        Args:
            checkpoint_dir: Directory to store stats file
        """
        self.checkpoint_dir = checkpoint_dir
        self.stats_file = os.path.join(checkpoint_dir, 'migration_stats.json')

        self.stats = {
            'total_records': 0,
            'processed_records': 0,
            'successful_records': 0,
            'failed_records': 0,
            'batches_processed': 0,
            'start_time': None,
            'end_time': None,
            'errors': []
        }

        self._load_stats()

    def _load_stats(self) -> None:
        """Load existing stats if available."""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    loaded_stats = json.load(f)
                    self.stats.update(loaded_stats)
            except (json.JSONDecodeError, IOError):
                pass

    def save_stats(self) -> None:
        """Save current stats to file."""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)

    def update(self, **kwargs) -> None:
        """
        Update stats with provided values.

        Args:
            **kwargs: Key-value pairs to update in stats
        """
        self.stats.update(kwargs)
        self.save_stats()

    def increment(self, field: str, value: int = 1) -> None:
        """
        Increment a numeric field.

        Args:
            field: Field name to increment
            value: Value to add (default: 1)
        """
        if field in self.stats:
            self.stats[field] += value
            self.save_stats()

    def add_error(self, error_msg: str, batch_number: Optional[int] = None) -> None:
        """
        Add an error to the error list.

        Args:
            error_msg: Error message
            batch_number: Optional batch number where error occurred
        """
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': error_msg
        }

        if batch_number is not None:
            error_entry['batch'] = batch_number

        self.stats['errors'].append(error_entry)
        self.stats['failed_records'] += 1
        self.save_stats()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get current statistics.

        Returns:
            Dictionary containing all stats
        """
        return self.stats.copy()

    def print_summary(self) -> None:
        """Print a summary of migration statistics."""
        print("\n" + "="*60)
        print("MIGRATION STATISTICS")
        print("="*60)
        print(f"Total Records:      {self.stats['total_records']:>15,}")
        print(f"Processed:          {self.stats['processed_records']:>15,}")
        print(f"Successful:         {self.stats['successful_records']:>15,}")
        print(f"Failed:             {self.stats['failed_records']:>15,}")
        print(f"Batches Processed:  {self.stats['batches_processed']:>15,}")

        if self.stats['start_time'] and self.stats['end_time']:
            start = datetime.fromisoformat(self.stats['start_time'])
            end = datetime.fromisoformat(self.stats['end_time'])
            duration = end - start
            print(f"Duration:           {str(duration).split('.')[0]:>15}")

        if self.stats['errors']:
            print(f"\nTotal Errors:       {len(self.stats['errors'])}")

        print("="*60 + "\n")
