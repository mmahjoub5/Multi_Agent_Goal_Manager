import httpx
from typing import Any, Dict, Optional
import requests

class ASYNC_APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(base_url=self.base_url)

    async def async_get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Send a GET request to the API.
        """
        try:
            response = self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise RuntimeError(f"An error occurred while making GET request: {e}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error occurred: {e.response.text}")

    async def async_post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Send a POST request to the API.
        """
        try:
            response = self.client.post(endpoint, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise RuntimeError(f"An error occurred while making POST request: {e}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error occurred: {e.response.text}")

    async def close(self):
        """
        Close the HTTP client session.
        """
        await self.client.close()


class SYNC_APIClient:
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the RequestsClient with a base URL and optional headers.
        """
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}

    def _make_url(self, endpoint: str) -> str:
        """
        Build the full URL for an endpoint.
        """
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Send a GET request.
        """
        url = self._make_url(endpoint)
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()  # Raise an error for non-2xx responses
            return response.json()
        except requests.RequestException as e:
            print(f"GET request error: {e}")
            raise

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Send a POST request.
        """
        url = self._make_url(endpoint)
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"POST request error: {e}")
            raise

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Send a PUT request.
        """
        url = self._make_url(endpoint)
        try:
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"PUT request error: {e}")
            raise

    def delete(self, endpoint: str) -> Dict:
        """
        Send a DELETE request.
        """
        url = self._make_url(endpoint)
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"DELETE request error: {e}")
            raise