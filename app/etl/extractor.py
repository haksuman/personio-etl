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
        """Fetches document categories/metadata for an employee."""
        logger.debug(f"Fetching document metadata for employee {employee_id}...")
        try:
            response = self.client.request("GET", f"company/employees/{employee_id}/documents")
            return response.get("data", [])
        except Exception as e:
            logger.warning(f"Failed to fetch documents for employee {employee_id}: {e}")
            return []
