import os
import mimetypes
from typing import List, Dict, Any
from app.api.personio_client import PersonioClient
from app.utils.logger import logger

class DocumentDownloader:
    """Downloads employee documents from Personio API."""
    
    def __init__(self, client: PersonioClient, output_base_path: str):
        self.client = client
        self.output_base_path = os.path.join(output_base_path, "documents")
        # Initialize mimetypes mapping
        mimetypes.init()
        # Add some common Personio types if they are missing
        mimetypes.add_type('application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx')
        mimetypes.add_type('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx')
        mimetypes.add_type('application/pdf', '.pdf')

        if not os.path.exists(self.output_base_path):
            os.makedirs(self.output_base_path, exist_ok=True)

    def download_for_employee(self, employee_id: int, document_metadata: List[Dict[str, Any]]):
        """Downloads all documents for a single employee."""
        if not document_metadata:
            logger.debug(f"No documents found in metadata for employee {employee_id}.")
            return

        employee_dir = os.path.join(self.output_base_path, str(employee_id))
        os.makedirs(employee_dir, exist_ok=True)
        
        logger.info(f"Downloading {len(document_metadata)} documents for employee {employee_id}...")
        
        for doc in document_metadata:
            # Personio V2 doc object has 'id', 'name', 'size', and 'document_type' (MIME)
            doc_id = doc.get("id")
            if not doc_id:
                logger.warning(f"Document object missing 'id' for employee {employee_id}: {doc}")
                continue

            filename = doc.get("name", f"document_{doc_id}")
            mime_type = doc.get("document_type")
            remote_size = doc.get("size")
            
            # Check if filename already has an extension
            _, existing_ext = os.path.splitext(filename)
            
            # If no extension in filename, try to guess from document_type
            if not existing_ext and mime_type:
                guessed_ext = mimetypes.guess_extension(mime_type)
                if guessed_ext:
                    filename = f"{filename}{guessed_ext}"
                    logger.debug(f"Guessed extension {guessed_ext} for MIME type {mime_type}")
            
            # Clean filename but preserve the dot for extension
            name_part, ext_part = os.path.splitext(filename)
            name_part = "".join([c for c in name_part if c.isalnum() or c in "_- "]).strip()
            # Ensure extension part is also clean (though usually it is)
            ext_part = "".join([c for c in ext_part if c.isalnum() or c == "."]).strip()
            
            filename = f"{name_part}{ext_part}"
            
            if not filename or filename == ".":
                filename = f"document_{doc_id}{ext_part if ext_part else ''}"
            
            save_path = os.path.join(employee_dir, filename)

            # Check if file exists and size matches
            if os.path.exists(save_path):
                local_size = os.path.getsize(save_path)
                if remote_size is not None and local_size == remote_size:
                    logger.info(f"Skipping download, file already exists and size matches: {filename}")
                    continue
                elif remote_size is None:
                    logger.info(f"Skipping download, file already exists: {filename} (remote size not available)")
                    continue
                else:
                    logger.info(f"File exists but size mismatch (Local: {local_size}, Remote: {remote_size}). Re-downloading: {filename}")
            
            try:
                # The endpoint for downloading a specific document in V2
                # v2/document-management/documents/{document_id}/download
                download_endpoint = f"v2/document-management/documents/{doc_id}/download"
                # V2 download requires Accept: */* (handled by default in client.download_file)
                logger.debug(f"Attempting download of {filename} (ID: {doc_id}) to {save_path}")
                self.client.download_file(download_endpoint, save_path)
                logger.info(f"Successfully downloaded document: {filename}")
            except Exception as e:
                logger.warning(f"Failed to download document {doc_id} for employee {employee_id}: {e}")
