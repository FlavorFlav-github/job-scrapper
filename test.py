from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json


# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument("--disable-gpu")  # (optional) To avoid some issues on Windows
chrome_options.add_argument("--no-sandbox")  # (optional) Useful for running in Docker
chrome_options.add_argument("--disable-dev-shm-usage")  # (optional) To avoid some memory issues
# Set up logging preferences directly in Chrome options
chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

driver = webdriver.Chrome(options=chrome_options)

# Now you can proceed with opening pages and capturing network logs as in the previous example
driver.get("https://linkedin.com")  # Replace with your target URL

# Your existing network requests capturing code goes here
# Function to capture network requests


# Fetch network requests
requests = get_network_requests()
for req in requests:
    print(req)

# Close the driver after completion
driver.quit()