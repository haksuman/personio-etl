import os
from typing import List, Dict, Any
from app.api.personio_client import PersonioClient
from app.utils.logger import logger

class DocumentDownloader:
    """Downloads employee documents from Personio API."""
    
    def __init__(self, client: PersonioClient, output_base_path: str):
        self.client = client
        self.output_base_path = os.path.join(output_base_path, "documents")
        if not os.path.exists(self.output_base_path):
            os.makedirs(self.output_base_path, exist_ok=True)

    def download_for_employee(self, employee_id: int, document_metadata: List[Dict[str, Any]]):
        """Downloads all documents for a single employee."""
        if not document_metadata:
            return

        employee_dir = os.path.join(self.output_base_path, str(employee_id))
        os.makedirs(employee_dir, exist_ok=True)
        
        logger.info(f"Downloading {len(document_metadata)} documents for employee {employee_id}...")
        
        for doc in document_metadata:
            # Personio doc object usually has 'id', 'title', 'extension', 'category'
            doc_id = doc.get("id")
            title = doc.get("title", f"document_{doc_id}")
            ext = doc.get("extension", "").strip(".")
            filename = f"{title}.{ext}" if ext else title
            
            # Clean filename
            filename = "".join([c for c in filename if c.isalnum() or c in "._- "]).strip()
            
            save_path = os.path.join(employee_dir, filename)
            
            try:
                # The endpoint for downloading a specific document
                # company/employees/{employee_id}/documents/{document_id}/download
                download_endpoint = f"company/employees/{employee_id}/documents/{doc_id}/download"
                self.client.download_file(download_endpoint, save_path)
            except Exception as e:
                logger.warning(f"Failed to download document {doc_id} for employee {employee_id}: {e}")
