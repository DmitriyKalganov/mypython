"""
Configuration module for ETL migration from BigQuery to Apache Unomi.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for ETL migration settings."""

    # BigQuery settings
    BIGQUERY_PROJECT_ID = os.getenv('BIGQUERY_PROJECT_ID')
    BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET')
    BIGQUERY_TABLE = os.getenv('BIGQUERY_TABLE', 'events_table')
    BIGQUERY_CREDENTIALS_PATH = os.getenv('BIGQUERY_CREDENTIALS_PATH')

    # Apache Unomi REST API settings
    UNOMI_API_URL = os.getenv('UNOMI_API_URL', 'http://localhost:8181')
    UNOMI_API_USERNAME = os.getenv('UNOMI_API_USERNAME', 'karaf')
    UNOMI_API_PASSWORD = os.getenv('UNOMI_API_PASSWORD', 'karaf')
    UNOMI_SCOPE = os.getenv('UNOMI_SCOPE', 'default')

    # Migration settings
    BATCH_SIZE = int(os.getenv('MIGRATION_BATCH_SIZE', '1000'))
    MAX_WORKERS = int(os.getenv('MIGRATION_MAX_WORKERS', '4'))
    RATE_LIMIT_REQUESTS_PER_SECOND = int(os.getenv('RATE_LIMIT_RPS', '10'))

    # Retry settings
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_WAIT_EXPONENTIAL_MULTIPLIER = int(os.getenv('RETRY_WAIT_MULTIPLIER', '2'))
    RETRY_WAIT_MIN_SECONDS = int(os.getenv('RETRY_WAIT_MIN', '1'))
    RETRY_WAIT_MAX_SECONDS = int(os.getenv('RETRY_WAIT_MAX', '60'))

    # Checkpoint settings
    CHECKPOINT_DIR = os.getenv('CHECKPOINT_DIR', './etl_migration/checkpoints')
    CHECKPOINT_INTERVAL = int(os.getenv('CHECKPOINT_INTERVAL', '1'))  # Save after N batches

    # Logging settings
    LOG_DIR = os.getenv('LOG_DIR', './etl_migration/logs')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Incremental sync settings
    WATERMARK_FILE = os.path.join(CHECKPOINT_DIR, 'watermark.json')
    SYNC_COLUMN = os.getenv('SYNC_COLUMN', 'date_ev')  # Column to use for incremental sync

    @classmethod
    def validate(cls):
        """Validate required configuration parameters."""
        required = [
            ('BIGQUERY_PROJECT_ID', cls.BIGQUERY_PROJECT_ID),
            ('BIGQUERY_DATASET', cls.BIGQUERY_DATASET),
            ('BIGQUERY_TABLE', cls.BIGQUERY_TABLE),
            ('UNOMI_API_URL', cls.UNOMI_API_URL),
        ]

        missing = [name for name, value in required if not value]

        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}. "
                "Please set these in your .env file."
            )

        return True

    @classmethod
    def display(cls):
        """Display current configuration (hiding sensitive data)."""
        config_items = [
            ('BigQuery Project', cls.BIGQUERY_PROJECT_ID),
            ('BigQuery Dataset', cls.BIGQUERY_DATASET),
            ('BigQuery Table', cls.BIGQUERY_TABLE),
            ('Unomi API URL', cls.UNOMI_API_URL),
            ('Batch Size', cls.BATCH_SIZE),
            ('Max Workers', cls.MAX_WORKERS),
            ('Rate Limit (req/s)', cls.RATE_LIMIT_REQUESTS_PER_SECOND),
            ('Max Retries', cls.MAX_RETRIES),
            ('Checkpoint Directory', cls.CHECKPOINT_DIR),
            ('Log Directory', cls.LOG_DIR),
        ]

        print("\n" + "="*60)
        print("ETL MIGRATION CONFIGURATION")
        print("="*60)
        for name, value in config_items:
            print(f"{name:.<30} {value}")
        print("="*60 + "\n")
