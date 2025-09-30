# main.py
import logging
from datetime import datetime
import const
from communication.notification_service_dispatcher import send_event
from communication.job_filtering import send_filtered_jobs_notification
from glassdoor_scraper import GlassdoorScraper
from data.data_handling import JobRepository
from communication.job_filtering import JobFilter

import data.init_files as init_files

# Init required files and folders
init_files.init_files()

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Main execution function for the job search pipeline."""
    logger.info("--- Starting Job Search and Notification Pipeline ---")
    send_event('Begin Search of new jobs')

    # 1. SCALING & COLLECTION
    scraper = GlassdoorScraper(
        pages_url=const.JOB_TO_SEARCH,
        location_type_mapping=const.LOCATION_TYPE_MAPPING,
        chrome_options_list=const.CHROME_OPTIONS
    )

    try:
        new_raw_jobs = scraper.run()
    finally:
        scraper.close()

    logger.info(f"Scraping complete. Collected {len(new_raw_jobs)} raw job listings.")

    # 2. PROCESSING & PERSISTENCE
    repository = JobRepository(file_path=const.GLASSDOOR_JOBS_FILE)

    # Map, merge with existing, and prune old jobs from the file
    all_jobs_clean = repository.merge_and_prune(
        new_raw_jobs=new_raw_jobs,
        max_days_old=const.JOBS_PRUNING
    )

    # 3. FILTERING FOR NOTIFICATION
    jobs_to_notify = JobFilter.filter_for_notification(
        jobs=all_jobs_clean,
        hours_ago=const.JOBS_LOOKBACK,
        required_keywords=const.REQUIRED_KEYWORDS,
        excluded_keywords=const.EXCLUDED_KEYWORDS,
        allowed_languages=["fr", "en"]  # Example: only notify for FR/EN jobs
    )

    logger.info(f"Notification filter resulted in {len(jobs_to_notify)} new jobs to send.")

    # 4. NOTIFICATION
    # NOTE: The dependency on 'send_filtered_jobs_notification' should be reviewed.
    # It currently expects the full list, hour, keywords, and performs its own filtering.
    # We pass the already-filtered list and configuration for logging/context.

    # Assuming send_filtered_jobs_notification needs the full configuration 
    # and handles its own formatting/dispatching internally:
    send_filtered_jobs_notification(
        jobs_to_notify
    )

    logger.info("--- Pipeline Finished Successfully ---")


if __name__ == "__main__":
    main()