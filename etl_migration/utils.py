"""
Utility functions for ETL migration.
"""
import os
import logging
import time
from datetime import datetime
from typing import Any, Dict


def setup_logging(log_dir: str, log_level: str = 'INFO') -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        log_dir: Directory to store log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'migration_{timestamp}.log')

    # Create logger
    logger = logging.getLogger('etl_migration')
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logging initialized. Log file: {log_file}")

    return logger


def transform_bigquery_to_unomi_event(row: Dict[str, Any], scope: str = 'default') -> Dict[str, Any]:
    """
    Transform BigQuery row to Apache Unomi event format.

    BigQuery schema: id, user_id, type_ev, date_ev, status
    Unomi event format: https://unomi.apache.org/manual/latest/index.html#_events

    Args:
        row: Dictionary representing a BigQuery row
        scope: Unomi scope for the event

    Returns:
        Dictionary in Unomi event format
    """
    event = {
        'eventType': row.get('type_ev', 'unknown'),
        'scope': scope,
        'source': {
            'itemId': f"bigquery-migration-{row.get('id', 'unknown')}",
            'itemType': 'migration',
            'scope': scope
        },
        'target': {
            'itemId': str(row.get('user_id', 'unknown')),
            'itemType': 'profile',
            'scope': scope
        },
        'properties': {
            'bigquery_id': str(row.get('id', '')),
            'status': row.get('status', ''),
            'original_date': row.get('date_ev', '').isoformat() if hasattr(row.get('date_ev', ''), 'isoformat') else str(row.get('date_ev', ''))
        }
    }

    # Add timestamp
    if row.get('date_ev'):
        if hasattr(row['date_ev'], 'timestamp'):
            # If date_ev is a datetime object
            event['timeStamp'] = int(row['date_ev'].timestamp() * 1000)
        elif isinstance(row['date_ev'], str):
            # If date_ev is a string, parse it
            try:
                dt = datetime.fromisoformat(row['date_ev'].replace('Z', '+00:00'))
                event['timeStamp'] = int(dt.timestamp() * 1000)
            except:
                event['timeStamp'] = int(time.time() * 1000)
        else:
            event['timeStamp'] = int(time.time() * 1000)
    else:
        event['timeStamp'] = int(time.time() * 1000)

    return event


def calculate_eta(processed: int, total: int, elapsed_seconds: float) -> str:
    """
    Calculate estimated time to completion.

    Args:
        processed: Number of items processed
        total: Total number of items
        elapsed_seconds: Time elapsed in seconds

    Returns:
        Human-readable ETA string
    """
    if processed == 0:
        return "calculating..."

    rate = processed / elapsed_seconds
    remaining = total - processed

    if rate == 0:
        return "unknown"

    eta_seconds = remaining / rate

    hours = int(eta_seconds // 3600)
    minutes = int((eta_seconds % 3600) // 60)
    seconds = int(eta_seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes to human-readable string.

    Args:
        bytes_value: Number of bytes

    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def format_number(number: int) -> str:
    """
    Format number with thousands separator.

    Args:
        number: Integer to format

    Returns:
        Formatted string (e.g., "1,234,567")
    """
    return f"{number:,}"


class RateLimiter:
    """Simple rate limiter using token bucket algorithm."""

    def __init__(self, requests_per_second: int):
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Maximum number of requests per second
        """
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0
        self.last_request_time = 0

    def wait(self):
        """Wait if necessary to maintain rate limit."""
        if self.min_interval == 0:
            return

        current_time = time.time()
        elapsed = current_time - self.last_request_time

        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            time.sleep(sleep_time)

        self.last_request_time = time.time()


def validate_row(row: Dict[str, Any]) -> bool:
    """
    Validate that a row has all required fields.

    Args:
        row: Dictionary representing a data row

    Returns:
        True if valid, False otherwise
    """
    required_fields = ['id', 'user_id', 'type_ev', 'date_ev']

    for field in required_fields:
        if field not in row or row[field] is None:
            return False

    return True
