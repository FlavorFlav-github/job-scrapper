import os

from const import glassdoor_jobs_output_directory

def init_files():
    if not os.path.exists(glassdoor_jobs_output_directory):
        os.makedirs(glassdoor_jobs_output_directory, exist_ok=True)