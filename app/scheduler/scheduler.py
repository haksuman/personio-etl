from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.utils.logger import logger
from typing import Callable

class PersonioScheduler:
    """Manages scheduled ETL jobs."""
    
    def __init__(self, cron_expression: str):
        self.scheduler = BackgroundScheduler()
        self.cron_expression = cron_expression

    def add_job(self, func: Callable):
        """Adds the ETL job to the scheduler."""
        logger.info(f"Adding scheduled job with cron: {self.cron_expression}")
        self.scheduler.add_job(
            func,
            CronTrigger.from_crontab(self.cron_expression),
            id="personio_etl_job",
            replace_existing=True
        )

    def start(self):
        """Starts the scheduler."""
        logger.info("Starting scheduler...")
        self.scheduler.start()

    def stop(self):
        """Stops the scheduler."""
        logger.info("Stopping scheduler...")
        self.scheduler.shutdown()
