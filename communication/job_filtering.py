import logging
from datetime import datetime, timedelta
# The external dependency for the dispatcher is fine, but should be handled by a configuration map/factory
from communication.notification_service_dispatcher import send_event

logger = logging.getLogger(__name__)

# --- Helper Functions (Refactored from previous answer) ---
def _has_required_keyword(title, keywords):
    """Returns True if the title contains ANY of the required keywords (case-insensitive)."""
    title_lower = title.lower()
    return any(keyword.lower() in title_lower for keyword in keywords)


def _has_excluded_keyword(title, keywords):
    """Returns True if the title contains ANY of the excluded keywords (case-insensitive)."""
    title_lower = title.lower()
    return any(keyword.lower() in title_lower for keyword in keywords)


# --- Main Filter Class ---
class JobFilter:
    """Applies various filters to a list of jobs."""

    @staticmethod
    def filter_for_notification(
            jobs,
            hours_ago,
            required_keywords,
            excluded_keywords,
            allowed_languages=None
    ):
        """
        Filters jobs to find only those suitable for notification based on
        recency, keywords, and language.
        """

        cutoff_date = datetime.now() - timedelta(hours=hours_ago)
        filtered_list = []

        for job in jobs:
            # 1. Date Filter (New jobs only)
            published_date_str = job.get("job_published_date")
            if not published_date_str:
                continue

            try:
                # The date format needs to handle the millisecond part if present
                published_date = datetime.strptime(published_date_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                if published_date <= cutoff_date:
                    continue
            except ValueError:
                # Log error or skip if date format is wrong
                continue

                # 2. Keyword Filter (Title)
            title = job.get("job_title", "")
            if not _has_required_keyword(title, required_keywords):
                continue

            if _has_excluded_keyword(title, excluded_keywords):
                continue

            # 3. Language Filter (Optional/if present in job dict)
            if allowed_languages is not None:
                job_language = job.get("language")
                # Only filter if the language key exists and is not one of the allowed ones
                if job_language and job_language not in allowed_languages:
                    continue

            # If all checks pass
            filtered_list.append(job)

        return filtered_list

# --- Output/Notification Logic (Sender) ---
def send_filtered_jobs_notification(jobs):
    """
    Filters jobs and sends notifications for the new/relevant ones.

    This function is a high-level orchestration layer.

    Args:
        jobs (list): List of all job dictionaries.
    """


    logger.info(f"{len(jobs)} jobs corresponding to filters")

    # Send notifications for the filtered jobs
    for job in jobs:
        # Create a clean message format (This could be extracted to a separate Formatter)
        message = (
            f'{job["job_title"]}\n'
            f'{job["job_employer"]}\n'
            f'{job["job_location"]}\n'
            f'<a href="{job["job_url"]}">Go to job</a>'
        )

        # The communication service handles the actual channel sending (Telegram, Slack, etc.)
        send_event(message)