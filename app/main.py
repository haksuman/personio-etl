import os
import sys
import time
import multiprocessing
from waitress import serve
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
    start_time = time.time()
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
        logger.info("Stage 1/5: Extracting employee data from Personio API...")
        raw_employees = extractor.fetch_employees()
        
        # 2. Transform
        logger.info("Stage 2/5: Transforming raw JSON data into flattened structure...")
        flattened_employees = transformer.transform_employees(raw_employees)
        logger.info(f"Successfully transformed {len(flattened_employees)} employee records.")
        
        # 3. Load Main CSV
        logger.info("Stage 3/5: Saving transformed data to CSV...")
        loader.save_to_csv(flattened_employees, "personio_employee_export.csv")
        
        # 4. Post-Process (Department Summary)
        logger.info("Stage 4/5: Generating department-level summary statistics...")
        summary = post_processor.generate_department_summary(flattened_employees)
        loader.save_to_csv(summary, "department_summary.csv")
        
        # 5. Optional: Download Documents
        if config.export.include_documents:
            logger.info("Stage 5/5: Syncing employee documents...")
            downloader = DocumentDownloader(client, config.export.output_path)
            for i, emp in enumerate(raw_employees):
                # Check different possible ID locations in the employee object
                emp_id = (
                    emp.get("attributes", {}).get("id", {}).get("value") or 
                    emp.get("id") or 
                    emp.get("attributes", {}).get("id")
                )
                
                if emp_id:
                    logger.debug(f"Processing documents for employee {emp_id} ({i+1}/{len(raw_employees)})...")
                    doc_metadata = extractor.fetch_document_categories(emp_id)
                    if doc_metadata:
                        downloader.download_for_employee(emp_id, doc_metadata)
                else:
                    logger.warning(f"Could not extract ID for employee at index {i}")
        else:
            logger.info("Stage 5/5: Document syncing skipped (disabled in config).")
        
        duration = time.time() - start_time
        logger.info(f"--- Personio ETL Job Completed Successfully in {duration:.2f} seconds ---")
        
    except Exception as e:
        logger.error(f"ETL Job failed after {time.time() - start_time:.2f}s with error: {e}", exc_info=True)

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
        logger.info(f"Scheduler started successfully. Next job scheduled according to cron: {config.schedule.cron}")
        
        # Start Web Server (Health Check) using Waitress for production
        flask_app = create_app()
        
        # Waitress production options
        # We use a small number of threads as this is a lightweight health check server
        threads = (multiprocessing.cpu_count() * 2) + 1 if multiprocessing.cpu_count() > 0 else 4
        
        logger.info(f"Initializing health check server on 0.0.0.0:5000 with {threads} threads...")
        logger.info("Service is fully initialized and ready to handle requests.")
        serve(flask_app, host='0.0.0.0', port=5000, threads=threads)
    else:
        logger.info("Scheduling is disabled. Exiting...")

if __name__ == "__main__":
    main()
