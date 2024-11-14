from datetime import datetime, timedelta
import telegramBot
import const


def filter_new_added_jobs(jobs, fromHour, keywords_in, keyword_out):

    def check_keyword(mode, keywords, title):
        is_ok = False if mode == "in" else True
        for keyword in keywords:
            if keyword in title:
                is_ok = True if mode == "in" else False
                break
        return is_ok


    # Loading the jobs
    job_listing_loaded = jobs

    # Filtering the jobs to only have the one created in the last 12 hours
    current_date = datetime.now() - timedelta(hours=fromHour)
    filter_job_listings_on_date = [job for job in job_listing_loaded if "job_published_date" in job and (job["job_published_date"] is not None and job["job_published_date"] != "") and datetime.strptime(job["job_published_date"], '%Y-%m-%dT%H:%M:%S.%f') > current_date]

    # Adding the job title lower to filter on it
    for i in range(len(filter_job_listings_on_date)):
        filter_job_listings_on_date[i]["jobTitleLower"] = filter_job_listings_on_date[i]["job_title"].lower()

    # Filtering the job to only have the one including specific keywords in the job title
    acceptedTitle = keywords_in
    notAcceptedTitle = keyword_out
    filter_job_listings_filter_accepted_title = [job for job in filter_job_listings_on_date if check_keyword("in", acceptedTitle, job["jobTitleLower"])]
    filter_job_listings_filter_not_accepted_title = [job for job in filter_job_listings_filter_accepted_title if check_keyword("not in", notAcceptedTitle, job["jobTitleLower"])]
    return filter_job_listings_filter_not_accepted_title


def send_new_added_jobs(job_listing_loaded, fromHour):
    # Get the filtered jobs based on date and keywords
    filter_job_listings_filter_not_accepted_title = filter_new_added_jobs(job_listing_loaded, fromHour,
                                                                                               const.acceptedTitle,
                                                                                               const.notAcceptedTitle)

    print(f"{str(len(filter_job_listings_filter_not_accepted_title))} jobs corresponding to filters")

    # Send the new added jobs by telegram
    for job in filter_job_listings_filter_not_accepted_title:
        job_title = job["job_title"]
        employer_name = job["job_employer"]
        location = job["job_location"]
        joblink = job["job_url"]
        telegramBot.send_message(f'{job_title}\n{employer_name}\n{location}\n<a href="{joblink}">Go to job</a>')



