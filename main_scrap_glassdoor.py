from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import requests
import time
import check_new_added_jobs
import const
import jobs_read_write
import language_detector
import telegramBot


pages_url = const.pages_url

# Configure Selenium to use a headless browser
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36')

telegramBot.send_message('Begin Search of new jobs')

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)
job_listings = []
today = datetime.today()
cursor_loaded = []
for original_page in pages_url:
    # Target URL
    url = original_page.get("url")
    seo_extract = "-".join(elem for elem in (url.split("/")[-1].split("-")[:-1]))
    url_input_extract = ("_".join(elem for elem in (url.split("_")[1:]))).replace(".htm", "")
    keywords_limits = url_input_extract.split("_")[-1][2:].split(",")
    keywords_limit_down, keyword_limit_up = keywords_limits[0], keywords_limits[1]
    location_extract = ((url_input_extract.split(",")[1]).split("_")[1])[2:]
    location_type_raw = ((url_input_extract.split(",")[1]).split("_")[1])[:2]
    location_type = const.location_type_mapping[location_type_raw] if location_type_raw in const.location_type_mapping else "Other"
    keywords = seo_extract[int(keywords_limit_down):int(keyword_limit_up)]
    print("SEO:", seo_extract)
    print("URL input:", url_input_extract)
    print("Location ID:", location_extract)
    print("Loc Type:", location_type)
    print("Keywords:", keywords)
    print("------------")
    
    driver.get(url)

    # Wait for page to load and check if CAPTCHA is present
    time.sleep(5)

    # Get the page content
    page_content = driver.page_source

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(page_content, 'html.parser')

    # Find the script or element that contains the JSON (replace 'script' with the correct tag if needed)
    script_tag = soup.find('script', text=lambda x: x and '"token":' in x)

    if script_tag:
        # Extract the JSON part (or the relevant part of the text)
        json_text = script_tag.string.strip()

        if json_text is not None:
            # Parse the JSON text (or the part containing the token)
            try:
                json_data = json.loads(json_text)
                token_loaded = json_data.get("props").get("pageProps").get("token")
                cursor_loaded = json_data.get("props").get("pageProps").get("jobSearchPage").get("searchResultsData").get("jobListings").get("paginationCursors")
                jobs_found_part_1 = json_data.get("props").get("pageProps").get("apolloCache").get("ROOT_QUERY")
                for key, value in jobs_found_part_1.items():
                    if key.startswith("jobListings"):
                        job_listings_key = key
                        job_listings = job_listings + value.get("jobListings")
                        break
            except json.JSONDecodeError:
                print("Failed to parse JSON")
        else:
            print("Content is empty")
    else:
        print("Token not found")


    def get_jobs(token, cursor, page, seo, url_input, location_id, key_word, location_type):
        url = "https://www.glassdoor.fr/graph"

        payload = json.dumps([
            {
                "operationName": "JobSearchResultsQuery",
                "variables": {
                    "excludeJobListingIds": [],
                    "filterParams": [],
                    "keyword": key_word,
                    "locationId": location_id,
                    "locationType": location_type,
                    "numJobsToShow": 30,
                    "originalPageUrl": url,
                    "parameterUrlInput": url_input,
                    "pageType": "SERP",
                    "queryString": "",
                    "seoFriendlyUrlInput": seo,
                    "seoUrl": True,
                    "includeIndeedJobAttributes": False,
                    "pageCursor": cursor,
                    "pageNumber": page
                },
                "query": "query JobSearchResultsQuery($excludeJobListingIds: [Long!], $filterParams: [FilterParams], $keyword: String, $locationId: Int, $locationType: LocationTypeEnum, $numJobsToShow: Int!, $originalPageUrl: String, $pageCursor: String, $pageNumber: Int, $pageType: PageTypeEnum, $parameterUrlInput: String, $queryString: String, $seoFriendlyUrlInput: String, $seoUrl: Boolean, $includeIndeedJobAttributes: Boolean) {\n  jobListings(\n    contextHolder: {queryString: $queryString, pageTypeEnum: $pageType, searchParams: {excludeJobListingIds: $excludeJobListingIds, filterParams: $filterParams, keyword: $keyword, locationId: $locationId, locationType: $locationType, numPerPage: $numJobsToShow, pageCursor: $pageCursor, pageNumber: $pageNumber, originalPageUrl: $originalPageUrl, seoFriendlyUrlInput: $seoFriendlyUrlInput, parameterUrlInput: $parameterUrlInput, seoUrl: $seoUrl, searchType: SR, includeIndeedJobAttributes: $includeIndeedJobAttributes}}\n  ) {\n    companyFilterOptions {\n      id\n      shortName\n      __typename\n    }\n    filterOptions\n    indeedCtk\n    jobListings {\n      ...JobView\n      __typename\n    }\n    jobListingSeoLinks {\n      linkItems {\n        position\n        url\n        __typename\n      }\n      __typename\n    }\n    jobSearchTrackingKey\n    jobsPageSeoData {\n      pageMetaDescription\n      pageTitle\n      __typename\n    }\n    paginationCursors {\n      cursor\n      pageNumber\n      __typename\n    }\n    indexablePageForSeo\n    searchResultsMetadata {\n      searchCriteria {\n        implicitLocation {\n          id\n          localizedDisplayName\n          type\n          __typename\n        }\n        keyword\n        location {\n          id\n          shortName\n          localizedShortName\n          localizedDisplayName\n          type\n          __typename\n        }\n        __typename\n      }\n      footerVO {\n        countryMenu {\n          childNavigationLinks {\n            id\n            link\n            textKey\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      helpCenterDomain\n      helpCenterLocale\n      jobAlert {\n        jobAlertId\n        __typename\n      }\n      jobSerpFaq {\n        questions {\n          answer\n          question\n          __typename\n        }\n        __typename\n      }\n      jobSerpJobOutlook {\n        occupation\n        paragraph\n        heading\n        __typename\n      }\n      showMachineReadableJobs\n      __typename\n    }\n    serpSeoLinksVO {\n      relatedJobTitlesResults\n      searchedJobTitle\n      searchedKeyword\n      searchedLocationIdAsString\n      searchedLocationSeoName\n      searchedLocationType\n      topCityIdsToNameResults {\n        key\n        value\n        __typename\n      }\n      topEmployerIdsToNameResults {\n        key\n        value\n        __typename\n      }\n      topEmployerNameResults\n      topOccupationResults\n      __typename\n    }\n    totalJobsCount\n    __typename\n  }\n}\n\nfragment JobView on JobListingSearchResult {\n  jobview {\n    header {\n      indeedJobAttribute {\n        skills\n        extractedJobAttributes {\n          key\n          value\n          __typename\n        }\n        __typename\n      }\n      adOrderId\n      advertiserType\n      ageInDays\n      divisionEmployerName\n      easyApply\n      employer {\n        id\n        name\n        shortName\n        __typename\n      }\n      expired\n      organic\n      employerNameFromSearch\n      goc\n      gocConfidence\n      gocId\n      isSponsoredJob\n      isSponsoredEmployer\n      jobCountryId\n      jobLink\n      jobResultTrackingKey\n      normalizedJobTitle\n      jobTitleText\n      locationName\n      locationType\n      locId\n      needsCommission\n      payCurrency\n      payPeriod\n      payPeriodAdjustedPay {\n        p10\n        p50\n        p90\n        __typename\n      }\n      rating\n      salarySource\n      savedJobId\n      seoJobLink\n      __typename\n    }\n    job {\n      descriptionFragmentsText\n      importConfigId\n      jobTitleId\n      jobTitleText\n      listingId\n      __typename\n    }\n    jobListingAdminDetails {\n      cpcVal\n      importConfigId\n      jobListingId\n      jobSourceId\n      userEligibleForAdminJobDetails\n      __typename\n    }\n    overview {\n      shortName\n      squareLogoUrl\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"
            }
        ])
        headers = {
          'accept': '*/*',
          'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
          'apollographql-client-name': 'job-search-next',
          'apollographql-client-version': '7.59.8',
          'content-type': 'application/json',
          'gd-csrf-token': token,
          'origin': 'https://www.glassdoor.fr',
          'priority': 'u=1, i',
          'referer': 'https://www.glassdoor.fr/',
          'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
          'sec-ch-ua-mobile': '?0',
          'sec-ch-ua-platform': '"Windows"',
          'sec-fetch-dest': 'empty',
          'sec-fetch-mode': 'cors',
          'sec-fetch-site': 'same-origin',
          'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
          'x-gd-job-page': 'serp',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        
        return response.json()
        #print(response.text)
    cursor_processed = []
    while len(cursor_loaded) > 0:
        jobs = get_jobs(token_loaded, cursor_loaded[0].get("cursor"), cursor_loaded[0].get("pageNumber"),
                        seo_extract, url_input_extract, location_extract, keywords, location_type)
        current_cursor = cursor_loaded.pop(0)  # Remove and get the first element
        cursor_processed.append(current_cursor.get("pageNumber"))
        if len(jobs) > 0:
            data = jobs[0].get("data")
            if data is not None and "jobListings" in data:
                if data.get("jobListings", {}) is not None and "jobListings" in data.get("jobListings", {}):
                    job_listings = job_listings + data.get("jobListings", {}).get("jobListings", [])

                    # Ensure paginationCursors exist
                    new_cursors = data.get("jobListings", {}).get("paginationCursors", [])

                    for new_cursor in new_cursors:
                        pageNumber = new_cursor.get("pageNumber")
                        if pageNumber and pageNumber not in cursor_processed and not any(c.get("pageNumber") == pageNumber for c in cursor_loaded):
                            cursor_loaded.append(new_cursor)

# Add a datePosted attribute
for i in range(len(job_listings)):
    if "jobview" in job_listings[i] and job_listings[i]["jobview"]:
        if "header" in job_listings[i]["jobview"] and job_listings[i]["jobview"]["header"]:
            if "ageInDays" in job_listings[i]["jobview"]["header"] and job_listings[i]["jobview"]["header"]["ageInDays"]:
                job_listings[i]["datePosted"] = (today + timedelta(days=-(int(job_listings[i]["jobview"]["header"]["ageInDays"])-1)) + timedelta(hours=-1)).isoformat()
        if "job" in job_listings[i]["jobview"] and job_listings[i]["jobview"]["job"]:
            if "descriptionFragmentsText" in job_listings[i]["jobview"]["job"] and job_listings[i]["jobview"]["job"]["descriptionFragmentsText"]:
                job_listings[i]["language"], job_listings[i]["language_confidence"] = language_detector.detect_language_transformers(job_listings[i]["jobview"]["job"]["descriptionFragmentsText"])

# Load jobs from file
job_listing_loaded = jobs_read_write.read_glassdoor_jobs()

# Merging existing jobs with new jobs
for new_jobs in job_listings:
        found = 0
        for old_jobs in job_listing_loaded:
            if new_jobs["jobview"]["job"]["listingId"] == old_jobs["jobview"]["job"]["listingId"]:
                found = 1
                break
        if found == 0:
            job_listing_loaded.append(new_jobs)

current_date = datetime.now() - timedelta(days=45)
filter_job_listings_on_date = [job for job in job_listing_loaded if "datePosted" in job and (job["datePosted"] is not None and job["datePosted"] != "") and datetime.strptime(job["datePosted"], '%Y-%m-%dT%H:%M:%S.%f') > current_date]


# Saving the list of jobs to file
with open(const.glassdoor_jobs_output_file_link, "w") as f:
    json.dump(filter_job_listings_on_date, f)

# Remove jobs in german from list of notification
filter_job_listings_de = [job for job in filter_job_listings_on_date if ("language" not in job) or ("language" in job and (job["language"] == "fr" or job["language"] == "en"))]

# Send the notification for new jobs
check_new_added_jobs.send_new_added_jobs(filter_job_listings_de, const.new_jobs_lookback)

# Close the browser
driver.quit()
