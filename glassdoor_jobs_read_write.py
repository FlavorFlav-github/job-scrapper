import json
import const


def read_glassdoor_jobs():
    try:
        with open(const.output_file_link, "r") as f:
            job_listing_loaded = json.load(f)
    except Exception as e:
        print("Could not read the file job_listings_glassdoor.json", e)
        job_listing_loaded = []
    return job_listing_loaded
