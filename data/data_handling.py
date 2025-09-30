import json
import logging
import re
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError

# Use logging instead of print for errors in library/reusable code
logger = logging.getLogger(__name__)


def read_jobs_from_file(file_path):
    """
    Reads and parses a list of job listings from a specified JSON file path.

    Args:
        file_path (str): The full path to the JSON file containing the job listings.

    Returns:
        list: The list of loaded job dictionaries, or an empty list if loading fails.
    """
    job_listing_loaded = []

    try:
        with open(file_path, "r") as f:
            job_listing_loaded = json.load(f)
            logger.info(f"Successfully loaded {len(job_listing_loaded)} jobs from {file_path}")

    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}. Returning empty list.")
    except JSONDecodeError as e:
        # File exists but is malformed/empty JSON
        logger.error(f"Could not decode JSON from {file_path}: {e}")
    except IOError as e:
        # Handles other IO errors (permissions, etc.)
        logger.error(f"An I/O error occurred while reading {file_path}: {e}")
    except Exception as e:
        # Catch unexpected errors, but keep the scope narrow
        logger.critical(f"An unexpected error occurred reading job file {file_path}: {e}")

    return job_listing_loaded


def write_jobs_to_file(file_path, jobs):
    """Writes the list of jobs back to the specified file path."""
    try:
        with open(file_path, "w") as f:
            json.dump(jobs, f, indent=4)
        logger.info(f"Successfully saved {len(jobs)} jobs to {file_path}")
    except IOError as e:
        logger.error(f"Failed to write jobs to {file_path}: {e}")


# --- Data Transformation ---
def map_raw_glassdoor_job(raw_job, today_date):
    """Maps a raw Glassdoor job dictionary to the project's standardized format."""

    job = {
        "job_id": raw_job["jobview"]["job"]["listingId"],
        "job_title": raw_job["jobview"]["header"]["jobTitleText"],
        "job_city": raw_job["jobview"]["header"]["locationName"],
        "job_url": f'https://www.glassdoor.fr/{raw_job["jobview"]["header"]["jobLink"]}',
        "job_description": raw_job["jobview"]["job"]["descriptionFragmentsText"][0] if raw_job["jobview"]["job"][
            "descriptionFragmentsText"] else None,
        "job_industry": None,
        "job_function": None,
        "job_location": raw_job["jobview"]["header"]["locationName"],
        "job_level": None,
        "job_employment_status": None,
        "job_origin": "Glassdoor"
    }

    header = raw_job["jobview"]["header"]
    overview = raw_job["jobview"]["overview"]

    # Calculate published date
    age_in_days = header.get("ageInDays")
    if age_in_days is not None:
        # Subtract age in days, plus a small buffer for time zone/time of day accuracy
        published_date = today_date - timedelta(days=int(age_in_days) - 1)
        job["job_published_date"] = published_date.isoformat()

    # Determine employer name
    if overview and overview.get("shortName"):
        job["job_employer"] = overview["shortName"]
    else:
        job["job_employer"] = header.get("employerNameFromSearch")

    return job

def extract_glassdoor_props(raw_text):
    pattern = r'null,\s*(\{.*?\})\]\\n"'

    match = re.search(pattern, raw_text)

    if match:
        # The content of the JSON object is in the first capture group (group 1)
        json_string = match.group(1)

        # 2. Convert the string to a Python dictionary (if needed)
        try:
            first = json.loads(f'"{json_string}"')  # wrap in quotes so Python sees it as a JSON string
            json_object = json.loads(first)
            return json_object
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding extracted JSON: {e}")
    else:
        logger.warning("JSON object not found in the text.")
    return None

# --- Repository/Merging Logic ---
class JobRepository:
    """Manages loading, merging, and pruning of job listings."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.today = datetime.today()

    def merge_and_prune(self, new_raw_jobs, max_days_old):
        """
        1. Maps new raw jobs to standard format.
        2. Merges them with existing jobs from the file.
        3. Prunes old jobs from the merged list.
        4. Saves the final list back to the file.

        Returns: The final list of jobs.
        """

        # 1. Map new jobs
        new_jobs_mapped = [
            map_raw_glassdoor_job(raw_job, self.today)
            for raw_job in new_raw_jobs
        ]

        # 2. Load and merge
        existing_jobs = read_jobs_from_file(self.file_path)

        # Use a set for quick lookup of existing job IDs
        existing_ids = {job["job_id"] for job in existing_jobs}

        merged_jobs = existing_jobs
        jobs_added = 0

        for new_job in new_jobs_mapped:
            if new_job["job_id"] not in existing_ids:
                merged_jobs.append(new_job)
                jobs_added += 1

        logger.info(f"Merged: Added {jobs_added} new unique jobs.")

        # 3. Prune old jobs
        cutoff_date = datetime.now() - timedelta(days=max_days_old)

        pruned_jobs = [
            job for job in merged_jobs
            if "job_published_date" in job
               and job["job_published_date"]
               and datetime.strptime(job["job_published_date"].split('.')[0], '%Y-%m-%dT%H:%M:%S') > cutoff_date
        ]

        jobs_pruned = len(merged_jobs) - len(pruned_jobs)
        logger.info(f"Pruned: Removed {jobs_pruned} old jobs (older than {max_days_old} days).")

        # 4. Save and return
        write_jobs_to_file(self.file_path, pruned_jobs)
        return pruned_jobs