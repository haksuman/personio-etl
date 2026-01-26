from typing import List, Dict, Any
from app.api.personio_client import PersonioClient
from app.utils.logger import logger

class PersonioExtractor:
    """Extracts various data entities from Personio API."""
    
    def __init__(self, client: PersonioClient):
        self.client = client

    def fetch_employees(self) -> List[Dict[str, Any]]:
        """Fetches all employee master data."""
        logger.info("Starting extraction of employee master data...")
        employees = self.client.get_paginated("company/employees")
        logger.info(f"Successfully fetched {len(employees)} employee records.")
        return employees

    def fetch_employment_details(self, employee_id: int) -> Dict[str, Any]:
        """Fetches employment details for a specific employee."""
        logger.debug(f"Fetching employment details for employee {employee_id}...")
        try:
            return self.client.request("GET", f"company/employees/{employee_id}/employment")
        except Exception as e:
            logger.warning(f"Failed to fetch employment details for employee {employee_id}: {e}")
            return {}

    def fetch_compensation(self, employee_id: int) -> Dict[str, Any]:
        """Fetches compensation data for a specific employee."""
        logger.debug(f"Fetching compensation for employee {employee_id}...")
        try:
            return self.client.request("GET", f"company/employees/{employee_id}/compensation")
        except Exception as e:
            logger.warning(f"Failed to fetch compensation for employee {employee_id}: {e}")
            return {}

    def fetch_document_categories(self, employee_id: int) -> List[Dict[str, Any]]:
        """Fetches document metadata for an employee using V2 API."""
        logger.debug(f"Fetching document metadata for employee {employee_id} using V2 API...")
        try:
            # V2 Document Management API uses owner_id to filter by employee
            params = {"owner_id": employee_id}
            response = self.client.request("GET", "v2/document-management/documents", params=params)
            
            # Personio API can sometimes wrap data in another layer or use pagination metadata
            data = response.get("_data", [])
            
            # Debug: log the response keys
            logger.debug(f"V2 Document Metadata response keys: {list(response.keys())}")
            
            if not data and "success" in response and response.get("success") is False:
                logger.error(f"API returned success=False for documents of employee {employee_id}")
                return []

            logger.info(f"Fetched metadata for {len(data)} documents for employee {employee_id}")
            return data
        except Exception as e:
            logger.warning(f"Failed to fetch documents for employee {employee_id} via V2: {e}")
            return []
