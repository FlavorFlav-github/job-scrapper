from datetime import datetime, date, timedelta
import telegramBot
import json
import requests
import time
import os


current_script_path = os.path.dirname(os.path.abspath(__file__))
Base_directory = current_script_path + os.path.sep
output_directory = f"{Base_directory}../glassdoor-scrap-jobs-data/"
output_file_link = f"{output_directory}job_listings_glassdoor.json"

def check_keyword(mode, keywords, title):
    is_ok = False if mode == "in" else True
    for keyword in keywords:
        if keyword in title:
            is_ok = True if mode == "in" else False
            break
    return is_ok

# Loading the jobs
job_listing_loaded = []
try:  
    with open(output_file_link, "r") as f:
        job_listing_loaded = json.load(f)
except Exception as e:
    print("Could not read the file job_listings_glassdoor.json", e)

# Filtering the jobs to only have the one created in the last 12 hours
current_date = datetime.now() - timedelta(hours=12) 
filter_job_listings_on_date = [job for job in job_listing_loaded if "datePosted" in job and (job["datePosted"] is not None and job["datePosted"] != "") and datetime.strptime(job["datePosted"], '%Y-%m-%dT%H:%M:%S.%f') > current_date]

# Adding the job title lower to filter on it
for i in range(len(filter_job_listings_on_date)):
    filter_job_listings_on_date[i]["jobTitleLower"] = filter_job_listings_on_date[i]["jobview"]["header"]["jobTitleText"].lower()

# Filtering the job to only have the one including specific keywords in the job title
acceptedTitle = ["data & analytics", "bi developer", "insight analyst", "data scientist", "insights analyst", "technical project manager", "business intelligence", "bi analyst", "data engineer", "bi engineer", "data analyst"]
notAcceptedTitle = ["senior"]
filter_job_listings_filter_accepted_title = [job for job in filter_job_listings_on_date if check_keyword("in", acceptedTitle, job["jobTitleLower"])]
filter_job_listings_filter_not_accepted_title = [job for job in filter_job_listings_filter_accepted_title if check_keyword("not in", notAcceptedTitle, job["jobTitleLower"])]

for job in filter_job_listings_filter_not_accepted_title:
    job_title = job["jobview"]["header"]["jobTitleText"]
    employer_name = job["jobview"]["header"]["employer"]["name"] if "name" in job["jobview"]["header"]["employer"] else job["jobview"]["header"]["employerNameFromSearch"]
    location = job["jobview"]["header"]["locationName"]
    joblink = job["jobview"]["header"]["jobLink"]
    joblink_c = f"https://www.glassdoor.fr/{joblink}"
    telegramBot.send_message(f'{job_title}\n{employer_name}\n{location}\n<a href="{joblink_c}">Go to job</a>')