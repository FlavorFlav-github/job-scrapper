# Glassdoor Jobs Scrapper

### 2024-10-24 - 1.1.2
#### Fixed
- Fixed published date calculation to start at 0 instead of 1
- Add extraction of location id, location type and keywords from source URL
- Reduced period of job lookback for notification to 6 hours aligned with cron execution

### 2024-10-23 - 1.1.1
#### Fixed
- Fixed save job loaded to only save jobs from 45 days of age max
  
### 2024-10-14 - 1.1.0
#### Added
- Add constants file for file location and keywords
- Add filter before saving jobs to only keep jobs from 45 days max
#### Modified
- Refactoring of function to send jobs by telegram
- Move pages url query detail in const file

### 2024-10-10 - 1.0.0
#### Added
- Add function scrapper that gets all jobs based on location and keyword filter
- Add function to save loaded jobs from scrapper
- Add function to send new jobs scrapped by telegram
