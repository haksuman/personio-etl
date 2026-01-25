import os
import sys
import time
from threading import Thread

# Add the current directory to sys.path to allow relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.config_loader import load_config
from app.api.personio_client import PersonioClient
from app.etl.extractor import PersonioExtractor
from app.etl.transformer import PersonioTransformer
from app.etl.loader import PersonioLoader
from app.etl.post_processor import PersonioPostProcessor
from app.documents.document_downloader import DocumentDownloader
from app.scheduler.scheduler import PersonioScheduler
from app.web.app import create_app
from app.utils.logger import logger, setup_logger

def run_etl_job():
    """Main ETL job orchestration."""
    try:
        logger.info("--- Starting Personio ETL Job ---")
        config = load_config()
        
        # Initialize client
        client = PersonioClient(
            client_id=config.personio.client_id,
            client_secret=config.personio.client_secret,
            base_url=config.personio.base_url
        )
        
        # ETL Steps
        extractor = PersonioExtractor(client)
        transformer = PersonioTransformer()
        loader = PersonioLoader(config.export.output_path)
        post_processor = PersonioPostProcessor()
        
        # 1. Extract
        raw_employees = extractor.fetch_employees()
        
        # 2. Transform
        logger.info("Transforming employee data...")
        flattened_employees = transformer.transform_employees(raw_employees)
        logger.info(f"Successfully transformed {len(flattened_employees)} employee records.")
        
        # 3. Load Main CSV
        logger.info("Loading employee data into CSV...")
        loader.save_to_csv(flattened_employees, "personio_employee_export.csv")
        
        # 4. Post-Process (Department Summary)
        logger.info("Generating and loading department summary...")
        summary = post_processor.generate_department_summary(flattened_employees)
        loader.save_to_csv(summary, "department_summary.csv")
        
        # 5. Optional: Download Documents
        if config.export.include_documents:
            logger.info("Starting document downloads...")
            downloader = DocumentDownloader(client, config.export.output_path)
            for i, emp in enumerate(raw_employees):
                emp_id = emp.get("attributes", {}).get("id", {}).get("value")
                if emp_id:
                    logger.info(f"Processing documents for employee {emp_id} ({i+1}/{len(raw_employees)})...")
                    doc_metadata = extractor.fetch_document_categories(emp_id)
                    downloader.download_for_employee(emp_id, doc_metadata)
        
        logger.info("--- Personio ETL Job Completed Successfully ---")
        
    except Exception as e:
        logger.error(f"ETL Job failed with error: {e}", exc_info=True)

def main():
    """Main entry point."""
    config = load_config()
    setup_logger(level=config.logging.level)
    
    logger.info("Starting Personio HR Data Export Integration")
    
    # Run once immediately
    run_etl_job()
    
    if config.schedule.enabled:
        # Start scheduler
        scheduler = PersonioScheduler(config.schedule.cron)
        scheduler.add_job(run_etl_job)
        scheduler.start()
        
        # Start Web Server (Health Check) in a separate thread
        flask_app = create_app()
        # In a real production environment, we'd use gunicorn
        # but for this lightweight tool, a simple Flask dev server or a Waitress server works.
        # We'll run it in the main thread (blocking) to keep the container alive.
        logger.info("Starting health check server on port 5000...")
        flask_app.run(host='0.0.0.0', port=5000, use_reloader=False)
    else:
        logger.info("Scheduling is disabled. Exiting...")

if __name__ == "__main__":
    main()
