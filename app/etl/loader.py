import csv
import os
from typing import List, Dict, Any
from app.utils.logger import logger
from app.utils.errors import FileWriteError

class PersonioLoader:
    """Loads transformed data into CSV files."""
    
    def __init__(self, output_path: str):
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path, exist_ok=True)

    def save_to_csv(self, data: List[Dict[str, Any]], filename: str):
        """Saves a list of dictionaries to a CSV file."""
        if not data:
            logger.warning(f"No data to save for {filename}")
            return

        file_path = os.path.join(self.output_path, filename)
        logger.info(f"Saving data to {file_path}...")
        
        try:
            fieldnames = data[0].keys()
            with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            logger.info(f"Successfully saved {len(data)} rows to {filename}")
        except Exception as e:
            raise FileWriteError(f"Failed to write CSV file {file_path}: {e}")
