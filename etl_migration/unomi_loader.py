"""
Apache Unomi data loader via REST API.
"""
import logging
import time
from typing import List, Dict, Any, Tuple
import requests
from requests.auth import HTTPBasicAuth
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)


class UnomiLoader:
    """Load data into Apache Unomi via REST API."""

    def __init__(
        self,
        api_url: str,
        username: str,
        password: str,
        scope: str = 'default',
        max_retries: int = 3,
        retry_wait_multiplier: int = 2,
        retry_wait_min: int = 1,
        retry_wait_max: int = 60
    ):
        """
        Initialize Unomi loader.

        Args:
            api_url: Unomi API base URL
            username: API username
            password: API password
            scope: Unomi scope (default: 'default')
            max_retries: Maximum number of retries for failed requests
            retry_wait_multiplier: Multiplier for exponential backoff
            retry_wait_min: Minimum wait time between retries (seconds)
            retry_wait_max: Maximum wait time between retries (seconds)
        """
        self.api_url = api_url.rstrip('/')
        self.username = username
        self.password = password
        self.scope = scope
        self.max_retries = max_retries
        self.retry_wait_multiplier = retry_wait_multiplier
        self.retry_wait_min = retry_wait_min
        self.retry_wait_max = retry_wait_max

        self.logger = logging.getLogger('etl_migration.unomi')

        # Session for connection pooling
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(username, password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def test_connection(self) -> bool:
        """
        Test connection to Unomi API.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to get server info
            url = f"{self.api_url}/cxs/context.json"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                self.logger.info("Successfully connected to Unomi API")
                return True
            else:
                self.logger.error(
                    f"Failed to connect to Unomi API. Status: {response.status_code}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=1, max=60),
        retry=retry_if_exception_type((requests.RequestException, ConnectionError))
    )
    def _send_event(self, event: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Send a single event to Unomi.

        Args:
            event: Event dictionary in Unomi format

        Returns:
            Tuple of (success: bool, message: str)
        """
        url = f"{self.api_url}/eventService/events"

        try:
            response = self.session.post(url, json=event, timeout=30)

            if response.status_code in [200, 201, 204]:
                return True, "Success"
            elif response.status_code == 400:
                return False, f"Bad request: {response.text}"
            elif response.status_code == 401:
                return False, "Authentication failed"
            elif response.status_code == 429:
                # Rate limit exceeded
                self.logger.warning("Rate limit exceeded, backing off...")
                time.sleep(5)
                raise requests.RequestException("Rate limit exceeded")
            else:
                return False, f"HTTP {response.status_code}: {response.text}"

        except requests.Timeout:
            self.logger.warning("Request timeout, retrying...")
            raise
        except requests.ConnectionError as e:
            self.logger.warning(f"Connection error: {e}, retrying...")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error sending event: {e}")
            return False, str(e)

    def load_batch(
        self,
        events: List[Dict[str, Any]]
    ) -> Tuple[int, int, List[Dict[str, Any]]]:
        """
        Load a batch of events to Unomi.

        Args:
            events: List of event dictionaries

        Returns:
            Tuple of (successful_count, failed_count, failed_events)
        """
        successful = 0
        failed = 0
        failed_events = []

        for i, event in enumerate(events):
            try:
                success, message = self._send_event(event)

                if success:
                    successful += 1
                    self.logger.debug(f"Event {i+1}/{len(events)} sent successfully")
                else:
                    failed += 1
                    failed_events.append({
                        'event': event,
                        'error': message
                    })
                    self.logger.warning(
                        f"Failed to send event {i+1}/{len(events)}: {message}"
                    )

            except Exception as e:
                failed += 1
                failed_events.append({
                    'event': event,
                    'error': str(e)
                })
                self.logger.error(f"Exception sending event {i+1}/{len(events)}: {e}")

        return successful, failed, failed_events

    def load_batch_bulk(
        self,
        events: List[Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        Load multiple events in a single bulk request (if Unomi supports it).
        Note: Standard Unomi API processes events individually.
        This method is provided for potential custom bulk endpoints.

        Args:
            events: List of event dictionaries

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Note: This is a placeholder for bulk operations
        # Standard Unomi doesn't have a bulk event endpoint
        # You may need to modify this based on your Unomi configuration

        self.logger.warning(
            "Bulk loading not supported by standard Unomi API. "
            "Falling back to individual event loading."
        )

        successful, failed, failed_events = self.load_batch(events)

        if failed == 0:
            return True, f"All {successful} events loaded successfully"
        else:
            return False, f"Loaded {successful} events, {failed} failed"

    def create_profile(self, profile_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Create or update a profile in Unomi.

        Args:
            profile_data: Profile data dictionary

        Returns:
            Tuple of (success: bool, message: str)
        """
        url = f"{self.api_url}/cxs/profiles"

        try:
            response = self.session.post(url, json=profile_data, timeout=30)

            if response.status_code in [200, 201]:
                return True, "Profile created/updated"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"

        except Exception as e:
            self.logger.error(f"Failed to create profile: {e}")
            return False, str(e)

    def get_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Get a profile from Unomi.

        Args:
            profile_id: Profile ID

        Returns:
            Profile data dictionary, or None if not found
        """
        url = f"{self.api_url}/cxs/profiles/{profile_id}"

        try:
            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                self.logger.error(
                    f"Failed to get profile: HTTP {response.status_code}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Error getting profile: {e}")
            return None

    def verify_event_loaded(self, event_id: str) -> bool:
        """
        Verify if an event was successfully loaded.

        Args:
            event_id: Event ID to verify

        Returns:
            True if event exists, False otherwise
        """
        # Note: This depends on your Unomi configuration
        # Unomi may not provide a direct way to query individual events
        # You might need to query by profile and event type

        self.logger.warning(
            "Event verification not implemented. "
            "Unomi doesn't provide a standard endpoint for individual event lookup."
        )
        return True

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics from Unomi (if available).

        Returns:
            Dictionary with stats, or empty dict if not available
        """
        try:
            # Try to get some basic info
            url = f"{self.api_url}/cxs/context.json"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'connected': True,
                    'scope': self.scope,
                    'server_info': data
                }
            else:
                return {'connected': False}

        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {'connected': False, 'error': str(e)}

    def close(self):
        """Close the session."""
        self.session.close()
        self.logger.info("Unomi loader session closed")
