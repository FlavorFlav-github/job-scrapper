# glassdoor_scraper.py
import json
import requests
import time
import logging
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import const
from data.data_handling import extract_glassdoor_props
from utils.chrome_scraper import Scraper

logger = logging.getLogger(__name__)

URL_SEARCH = "https://www.glassdoor.fr/Emploi/search"
# --- Constants (GraphQL Query) ---
# NOTE: This massive string must be kept separate for readability.
GLASSDOOR_GRAPHQL_QUERY = """
query JobSearchResultsQuery($excludeJobListingIds: [Long!], $filterParams: [FilterParams], $keyword: String, $locationId: Int, $locationType: LocationTypeEnum, $numJobsToShow: Int!, $originalPageUrl: String, $pageCursor: String, $pageNumber: Int, $pageType: PageTypeEnum, $parameterUrlInput: String, $queryString: String, $seoFriendlyUrlInput: String, $seoUrl: Boolean, $includeIndeedJobAttributes: Boolean) {\n jobListings(\n contextHolder: {queryString: $queryString, pageTypeEnum: $pageType, searchParams: {excludeJobListingIds: $excludeJobListingIds, filterParams: $filterParams, keyword: $keyword, locationId: $locationId, locationType: $locationType, numPerPage: $numJobsToShow, pageCursor: $pageCursor, pageNumber: $pageNumber, originalPageUrl: $originalPageUrl, seoFriendlyUrlInput: $seoFriendlyUrlInput, parameterUrlInput: $parameterUrlInput, seoUrl: $seoUrl, searchType: SR, includeIndeedJobAttributes: $includeIndeedJobAttributes}}\n ) {\n companyFilterOptions {\n id\n shortName\n __typename\n }\n filterOptions\n indeedCtk\n jobListings {\n ...JobView\n __typename\n }\n jobListingSeoLinks {\n linkItems {\n position\n url\n __typename\n }\n __typename\n }\n jobSearchTrackingKey\n jobsPageSeoData {\n pageMetaDescription\n pageTitle\n __typename\n }\n paginationCursors {\n cursor\n pageNumber\n __typename\n }\n indexablePageForSeo\n searchResultsMetadata {\n searchCriteria {\n implicitLocation {\n id\n localizedDisplayName\n type\n __typename\n }\n keyword\n location {\n id\n shortName\n localizedShortName\n localizedDisplayName\n type\n __typename\n }\n __typename\n }\n footerVO {\n countryMenu {\n childNavigationLinks {\n id\n link\n textKey\n __typename\n }\n __typename\n }\n __typename\n }\n helpCenterDomain\n helpCenterLocale\n jobAlert {\n jobAlertId\n __typename\n }\n jobSerpFaq {\n questions {\n answer\n question\n __typename\n }\n __typename\n }\n jobSerpJobOutlook {\n occupation\n paragraph\n heading\n __typename\n }\n showMachineReadableJobs\n __typename\n }\n serpSeoLinksVO {\n relatedJobTitlesResults\n searchedJobTitle\n searchedKeyword\n searchedLocationIdAsString\n searchedLocationSeoName\n searchedLocationType\n topCityIdsToNameResults {\n key\n value\n __typename\n }\n topEmployerIdsToNameResults {\n key\n value\n __typename\n }\n topEmployerNameResults\n topOccupationResults\n __typename\n }\n totalJobsCount\n __typename\n }\n}\n\nfragment JobView on JobListingSearchResult {\n jobview {\n header {\n indeedJobAttribute {\n skills\n extractedJobAttributes {\n key\n value\n __typename\n }\n __typename\n }\n adOrderId\n advertiserType\n ageInDays\n divisionEmployerName\n easyApply\n employer {\n id\n name\n shortName\n __typename\n }\n expired\n organic\n employerNameFromSearch\n goc\n gocConfidence\n gocId\n isSponsoredJob\n isSponsoredEmployer\n jobCountryId\n jobLink\n jobResultTrackingKey\n normalizedJobTitle\n jobTitleText\n locationName\n locationType\n locId\n needsCommission\n payCurrency\n payPeriod\n payPeriodAdjustedPay {\n p10\n p50\n p90\n __typename\n }\n rating\n salarySource\n savedJobId\n seoJobLink\n __typename\n }\n job {\n descriptionFragmentsText\n importConfigId\n jobTitleId\n jobTitleText\n listingId\n __typename\n }\n jobListingAdminDetails {\n cpcVal\n importConfigId\n jobListingId\n jobSourceId\n userEligibleForAdminJobDetails\n __typename\n }\n overview {\n shortName\n squareLogoUrl\n __typename\n }\n __typename\n }\n __typename\n}\n
"""


class GlassdoorAPIClient:
    """Handles direct API calls to Glassdoor's GraphQL endpoint."""

    def __init__(self, token):
        self.base_url = "https://www.glassdoor.fr/graph"
        self.token = token
        self.headers = {
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

    def get_jobs(self, cursor, page_number, params):
        """Fetches jobs for a single page using the API."""

        variables = {
            "excludeJobListingIds": [],
            "filterParams": [],
            "numJobsToShow": 30,
            "pageType": "SERP",
            "seoUrl": True,
            "includeIndeedJobAttributes": False,
            "pageCursor": cursor,
            "pageNumber": page_number,
            **params
        }

        payload = json.dumps([{
            "operationName": "JobSearchResultsQuery",
            "variables": variables,
            "query": GLASSDOOR_GRAPHQL_QUERY
        }])

        try:
            response = requests.post(self.base_url, headers=self.headers, data=payload, timeout=30)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed for page {page_number}: {e}")
            return None


class GlassdoorScraper:
    """Orchestrates the scraping, token extraction, and pagination."""

    def __init__(self, pages_url, location_type_mapping, chrome_options_list):
        self.pages_url = pages_url
        self.location_type_mapping = location_type_mapping

        chrome_options = Options()
        for arg in chrome_options_list:
            chrome_options.add_argument(arg)

        self.scraper = Scraper(chrome_options)
        self.driver = self.scraper.driver
        self.api_client = None  # Initialized after token extraction
        self.all_job_listings = []

    def _extract_url(self, keyword, location):
        self.driver.get(URL_SEARCH)
        time.sleep(3)

        # Locate the keyword search element using its unique ID
        job_title_input = self.driver.find_element(By.ID, "searchBar-jobTitle")

        # Fill text
        job_title_input.clear()
        job_title_input.send_keys(keyword)

        # 1. Locate the location element using its unique ID
        location_input = self.driver.find_element(By.ID, "searchBar-location")

        # 2. Fill text
        location_input.clear()  # Clear existing text (e.g., "Paris, 75 (France)")
        location_input.send_keys(location)

        try:
            # Get the URL BEFORE the navigation
            old_url = self.driver.current_url

            # 3. Press the ENTER key on that input element
            location_input.send_keys(Keys.ENTER)

            # Wait until the URL is NOT the old one (i.e., navigation has occurred)
            WebDriverWait(self.driver, 10).until_not(
                EC.url_to_be(old_url)
            )

        except Exception:
            logger.warning("Timeout waiting for the new page to load or for the URL to change.")
            # If timeout occurs, proceed to get the current URL anyway

        url = self.driver.current_url

        # Cycle driver to avoid Cloudflare anti-bot
        self.scraper.cycle_driver()
        self.driver = self.scraper.driver

        return url

    def _parse_url_params(self, url):
        """Extracts dynamic parameters from the initial search URL."""
        # This is the tricky parsing from the original script - highly fragile!
        try:
            seo_extract = "-".join(elem for elem in (url.split("/")[-1].split("-")[:-1]))

            url_input_extract = ("_".join(elem for elem in (url.split("_")[1:]))).replace(".htm", "")

            keywords_limits = url_input_extract.split("_")[-1][2:].split(",")

            keywords_limit_down, keyword_limit_up = keywords_limits[0], keywords_limits[1]

            location_extract = ((url_input_extract.split(",")[1]).split("_")[1])[2:]

            location_type_raw = ((url_input_extract.split(",")[1]).split("_")[1])[:2]

            location_type = const.LOCATION_TYPE_MAPPING[
                location_type_raw] if location_type_raw in const.LOCATION_TYPE_MAPPING else "Other"

            keywords = seo_extract[int(keywords_limit_down):int(keyword_limit_up)]

            return {
                "seoFriendlyUrlInput": seo_extract,
                "parameterUrlInput": url_input_extract,
                "locationId": int(location_extract),
                "locationType": location_type,
                "keyword": keywords,
                "originalPageUrl": url,
            }
        except Exception as e:
            logger.error(f"Failed to parse complex URL: {url}. Error: {e}")
            return None

    def _extract_initial_data(self, url):
        """Navigates the page, extracts token, initial jobs, and pagination cursors."""
        self.driver.get(url)
        time.sleep(5)  # Wait for JS to render

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # Find the script tag containing the initial state JSON (Apollo Cache)
        script_tag = soup.find('script', text=lambda t: t and 'pageProps' in t)

        # Cycle driver to avoid Cloudflare anti-bot
        self.scraper.cycle_driver()
        self.driver = self.scraper.driver

        if not script_tag:
            logger.warning(f"Could not find initial JSON data for {url}")
            return None, None, None  # Token, Cursors, Initial Jobs

        json_data = extract_glassdoor_props(script_tag.string.strip())

        try:
            props = json_data.get("pageProps", {})
            token = props.get("token")

            job_search_page = props.get("jobSearchPage", {})
            results_data = job_search_page.get("searchResultsData", {})
            initial_jobs = results_data.get("jobListings", {}).get("jobListings", [])
            cursors = results_data.get("jobListings", {}).get("paginationCursors", [])

            return token, cursors, initial_jobs

        except (json.JSONDecodeError, AttributeError) as e:
            logger.error(f"Failed to parse initial JSON state for {url}: {e}")
            return None, None, None

    def run(self):
        """Runs the scraping process for all configured URLs."""

        for page_config in self.pages_url:
            keyword_search = page_config["keyword"]
            location_search = page_config["location"]
            url = self._extract_url(keyword_search, location_search)

            logger.info(f"Retreived url for keyword {keyword_search} and location {location_search} : {url}")

            # 1. Extract parameters and initial data
            params = self._parse_url_params(url)
            token, cursors_loaded, initial_jobs = self._extract_initial_data(url)

            if not token or not params:
                logger.error(f"Skipping {url} due to missing token or parameters.")
                continue

            self.api_client = GlassdoorAPIClient(token)
            self.all_job_listings.extend(initial_jobs)

            logger.info(f"Page {url}: Found {len(initial_jobs)} initial jobs. Starting pagination.")

            # 2. Paginate using API
            cursor_processed = set()
            while cursors_loaded:
                current_cursor = cursors_loaded.pop(0)
                page_number = current_cursor.get("pageNumber")
                cursor_string = current_cursor.get("cursor")

                if page_number in cursor_processed:
                    continue

                jobs_response = self.api_client.get_jobs(cursor_string, page_number, params)

                if jobs_response and len(jobs_response) > 0:
                    data = jobs_response[0].get("data")
                    if data and data.get("jobListings"):
                        # Add new jobs
                        new_jobs = data["jobListings"].get("jobListings", [])
                        self.all_job_listings.extend(new_jobs)

                        # Add new cursors to the queue
                        new_cursors = data["jobListings"].get("paginationCursors", [])
                        for new_cursor in new_cursors:
                            if new_cursor["pageNumber"] not in cursor_processed and new_cursor not in cursors_loaded:
                                cursors_loaded.append(new_cursor)

                cursor_processed.add(page_number)
                time.sleep(1)  # Be polite

        return self.all_job_listings

    def close(self):
        """Closes the Selenium WebDriver."""
        try:
            self.driver.quit()
        except Exception:
            pass  # Already closed