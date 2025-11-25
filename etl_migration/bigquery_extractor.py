"""
BigQuery data extractor for ETL migration.
"""
import logging
from typing import Iterator, List, Dict, Any, Optional
from google.cloud import bigquery
from google.oauth2 import service_account


class BigQueryExtractor:
    """Extract data from BigQuery in batches."""

    def __init__(
        self,
        project_id: str,
        dataset: str,
        table: str,
        credentials_path: Optional[str] = None
    ):
        """
        Initialize BigQuery extractor.

        Args:
            project_id: GCP project ID
            dataset: BigQuery dataset name
            table: BigQuery table name
            credentials_path: Path to service account JSON file (optional)
        """
        self.project_id = project_id
        self.dataset = dataset
        self.table = table
        self.logger = logging.getLogger('etl_migration.bigquery')

        # Initialize BigQuery client
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self.client = bigquery.Client(
                project=project_id,
                credentials=credentials
            )
        else:
            # Use application default credentials
            self.client = bigquery.Client(project=project_id)

        self.table_ref = f"{project_id}.{dataset}.{table}"

    def get_total_rows(self) -> int:
        """
        Get total number of rows in the table.

        Returns:
            Total row count
        """
        query = f"SELECT COUNT(*) as total FROM `{self.table_ref}`"

        try:
            result = self.client.query(query).result()
            total = list(result)[0]['total']
            self.logger.info(f"Total rows in {self.table_ref}: {total:,}")
            return total
        except Exception as e:
            self.logger.error(f"Failed to get row count: {e}")
            raise

    def extract_batch(
        self,
        batch_size: int,
        offset: int,
        order_by: str = 'id'
    ) -> List[Dict[str, Any]]:
        """
        Extract a batch of data from BigQuery.

        Args:
            batch_size: Number of rows to extract
            offset: Offset for pagination
            order_by: Column to order by (default: 'id')

        Returns:
            List of dictionaries representing rows
        """
        query = f"""
            SELECT id, user_id, type_ev, date_ev, status
            FROM `{self.table_ref}`
            ORDER BY {order_by}
            LIMIT {batch_size}
            OFFSET {offset}
        """

        try:
            self.logger.debug(f"Extracting batch: offset={offset}, size={batch_size}")
            result = self.client.query(query).result()

            rows = []
            for row in result:
                rows.append({
                    'id': row.id,
                    'user_id': row.user_id,
                    'type_ev': row.type_ev,
                    'date_ev': row.date_ev,
                    'status': row.status
                })

            self.logger.debug(f"Extracted {len(rows)} rows")
            return rows

        except Exception as e:
            self.logger.error(f"Failed to extract batch at offset {offset}: {e}")
            raise

    def extract_all_batches(
        self,
        batch_size: int,
        start_offset: int = 0,
        order_by: str = 'id'
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Generator that yields batches of data.

        Args:
            batch_size: Number of rows per batch
            start_offset: Starting offset (for resuming)
            order_by: Column to order by

        Yields:
            List of dictionaries for each batch
        """
        total_rows = self.get_total_rows()
        offset = start_offset

        while offset < total_rows:
            try:
                batch = self.extract_batch(batch_size, offset, order_by)

                if not batch:
                    break

                yield batch
                offset += batch_size

            except Exception as e:
                self.logger.error(f"Error extracting batch at offset {offset}: {e}")
                raise

    def extract_incremental(
        self,
        watermark_column: str,
        watermark_value: Any,
        batch_size: int,
        order_by: Optional[str] = None
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Extract data incrementally based on watermark.

        Args:
            watermark_column: Column to use for watermark (e.g., 'date_ev')
            watermark_value: Last processed value
            batch_size: Number of rows per batch
            order_by: Column to order by (defaults to watermark_column)

        Yields:
            List of dictionaries for each batch
        """
        if order_by is None:
            order_by = watermark_column

        # Build query for incremental extraction
        query_base = f"""
            SELECT id, user_id, type_ev, date_ev, status
            FROM `{self.table_ref}`
            WHERE {watermark_column} > @watermark_value
            ORDER BY {order_by}
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter(
                    "watermark_value",
                    "STRING",  # Adjust type based on your column
                    str(watermark_value)
                )
            ]
        )

        try:
            self.logger.info(
                f"Extracting incremental data from {watermark_column} > {watermark_value}"
            )

            query_job = self.client.query(query_base, job_config=job_config)
            results = query_job.result()

            batch = []
            for row in results:
                batch.append({
                    'id': row.id,
                    'user_id': row.user_id,
                    'type_ev': row.type_ev,
                    'date_ev': row.date_ev,
                    'status': row.status
                })

                if len(batch) >= batch_size:
                    yield batch
                    batch = []

            # Yield remaining records
            if batch:
                yield batch

        except Exception as e:
            self.logger.error(f"Failed to extract incremental data: {e}")
            raise

    def get_max_value(self, column: str) -> Any:
        """
        Get the maximum value of a column.

        Args:
            column: Column name

        Returns:
            Maximum value
        """
        query = f"SELECT MAX({column}) as max_value FROM `{self.table_ref}`"

        try:
            result = self.client.query(query).result()
            max_value = list(result)[0]['max_value']
            self.logger.info(f"Max value of {column}: {max_value}")
            return max_value
        except Exception as e:
            self.logger.error(f"Failed to get max value: {e}")
            raise

    def validate_table_schema(self) -> bool:
        """
        Validate that the table has the expected schema.

        Returns:
            True if schema is valid
        """
        expected_columns = {'id', 'user_id', 'type_ev', 'date_ev', 'status'}

        try:
            table = self.client.get_table(self.table_ref)
            actual_columns = {field.name for field in table.schema}

            missing = expected_columns - actual_columns
            if missing:
                self.logger.error(f"Missing columns in table: {missing}")
                return False

            self.logger.info("Table schema validation passed")
            return True

        except Exception as e:
            self.logger.error(f"Failed to validate schema: {e}")
            return False

    def get_table_info(self) -> Dict[str, Any]:
        """
        Get information about the table.

        Returns:
            Dictionary containing table information
        """
        try:
            table = self.client.get_table(self.table_ref)

            info = {
                'num_rows': table.num_rows,
                'num_bytes': table.num_bytes,
                'created': table.created.isoformat() if table.created else None,
                'modified': table.modified.isoformat() if table.modified else None,
                'schema': [
                    {'name': field.name, 'type': field.field_type}
                    for field in table.schema
                ]
            }

            return info

        except Exception as e:
            self.logger.error(f"Failed to get table info: {e}")
            raise
