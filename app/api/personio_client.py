import os
import time
import requests
from typing import Optional, Dict, Any, List
from app.utils.logger import logger
from app.utils.errors import AuthenticationError, APIError

class PersonioClient:
    """Robust client for Personio API with OAuth, retries, and pagination."""
    
    def __init__(self, client_id: str, client_secret: str, base_url: str = "https://api.personio.de"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self.token_expires_at: float = 0
        self.session = requests.Session()

    def _authenticate(self):
        """Retrieves OAuth token from Personio."""
        url = f"{self.base_url}/v1/auth"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            logger.info("Authenticating with Personio API...")
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            # The Personio API usually returns token in 'data' field or directly
            # Based on standard Personio API docs, it's in data['token']
            if 'data' in data and 'token' in data['data']:
                self.token = data['data']['token']
                # Personio tokens usually last 1 hour
                self.token_expires_at = time.time() + 3500 
                logger.info("Successfully authenticated.")
            else:
                raise AuthenticationError(f"Unexpected token response structure: {data}")
                
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Failed to authenticate: {e}")

    def _ensure_token(self):
        """Checks token validity and refreshes if necessary."""
        if not self.token or time.time() >= self.token_expires_at:
            self._authenticate()

    def _get_headers(self, accept: str = "application/json") -> Dict[str, str]:
        self._ensure_token()
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": accept
        }

    def request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                json_data: Optional[Dict] = None, retries: int = 3,
                accept: str = "application/json") -> Dict[str, Any]:
        """Generic request method with retry logic and rate-limit awareness."""
        endpoint = endpoint.lstrip('/')
        if not (endpoint.startswith('v1/') or endpoint.startswith('v2/')):
            url = f"{self.base_url}/v1/{endpoint}"
        else:
            url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(retries):
            try:
                response = self.session.request(
                    method, 
                    url, 
                    headers=self._get_headers(accept=accept), 
                    params=params, 
                    json=json_data,
                    timeout=30
                )
                
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.warning(f"Rate limited (429). Retrying after {retry_after} seconds (Attempt {attempt + 1}/{retries})...")
                    time.sleep(retry_after)
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                # Handle 5xx errors with retry, but fail on 4xx (except 429)
                if response.status_code >= 500:
                    logger.warning(f"Server error {response.status_code} on attempt {attempt + 1}. Retrying...")
                    time.sleep(2 ** attempt)
                    continue
                raise APIError(f"API request failed with status {response.status_code}: {e}")
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt == retries - 1:
                    raise APIError(f"Network error after {retries} attempts: {e}")
                logger.warning(f"Network error on attempt {attempt + 1}: {e}. Retrying...")
                time.sleep(2 ** attempt)
            except requests.exceptions.RequestException as e:
                raise APIError(f"Unexpected request error: {e}")
        
        raise APIError(f"Max retries ({retries}) exceeded for {url}")

    def get_paginated(self, endpoint: str, params: Optional[Dict] = None, max_pages: int = 1000) -> List[Dict]:
        """Handles Personio API pagination with safety limits."""
        all_data = []
        current_params = params.copy() if params else {}
        current_params.setdefault("limit", 100)
        
        # Personio can use offset or page based pagination depending on the endpoint version
        # We start with offset=0
        current_params.setdefault("offset", 0)
        
        page_count = 0
        while page_count < max_pages:
            page_count += 1
            logger.debug(f"Fetching page {page_count} for {endpoint}...")
            
            response_data = self.request("GET", endpoint, params=current_params)
            
            # Personio API structure: {"success": True, "metadata": {...}, "data": [...]}
            # V2 API often uses _data and _meta
            data_list = response_data.get("data") or response_data.get("_data") or []
            
            if not data_list:
                logger.debug(f"No more data for {endpoint} at page {page_count}.")
                break
                
            if not isinstance(data_list, list):
                # Some endpoints might return a single object under 'data'
                all_data.append(data_list)
                logger.debug(f"Endpoint {endpoint} returned single object instead of list.")
                break
                
            all_data.extend(data_list)
            
            metadata = response_data.get("metadata") or response_data.get("_meta") or {}
            total_pages = metadata.get("total_pages", 1)
            current_page = metadata.get("current_page", 1)
            
            logger.info(f"Fetched page {current_page}/{total_pages} for {endpoint} ({len(all_data)} records so far)")
            
            if current_page >= total_pages:
                break
            
            # Update pagination parameters for next iteration
            # If current_page is present, we try to use it
            if "current_page" in metadata:
                current_params["page"] = current_page + 1
                # If they were using offset, we might need to remove it or update it
                # Personio API v1 typically uses offset/limit, but metadata returns pages
                if "offset" in current_params:
                    current_params["offset"] = len(all_data)
            else:
                # Fallback to offset if current_page is not available
                current_params["offset"] = len(all_data)
            
        if page_count >= max_pages:
            logger.warning(f"Reached max_pages limit ({max_pages}) for {endpoint}. Data might be incomplete.")
            
        return all_data

    def download_file(self, endpoint: str, save_path: str, accept: str = "*/*"):
        """Special method for binary data downloads."""
        endpoint = endpoint.lstrip('/')
        if not (endpoint.startswith('v1/') or endpoint.startswith('v2/')):
            url = f"{self.base_url}/v1/{endpoint}"
        else:
            url = f"{self.base_url}/{endpoint}"
            
        try:
            headers = self._get_headers(accept=accept)
            logger.debug(f"Downloading file from {url} with headers: {headers}")
            response = self.session.get(url, headers=headers, stream=True, timeout=60)
            
            # Log response info for debugging
            logger.debug(f"Download response status: {response.status_code}")
            logger.debug(f"Download response headers: {response.headers}")
            
            response.raise_for_status()
            
            # Ensure the directory exists before writing
            save_dir = os.path.dirname(save_path)
            if not os.path.exists(save_dir):
                logger.info(f"Creating directory: {save_dir}")
                os.makedirs(save_dir, exist_ok=True)
            
            logger.info(f"Writing binary data to: {save_path}")
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify file was written
            if os.path.exists(save_path):
                file_size = os.path.getsize(save_path)
                logger.info(f"Successfully saved {file_size} bytes to {save_path}")
            else:
                logger.error(f"File was not found after write attempt: {save_path}")
                
        except Exception as e:
            logger.error(f"Failed to download file from {url}: {e}")
            raise APIError(f"File download failed: {e}")
