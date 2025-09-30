from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Scraper:
    def __init__(self, options):
        self.chrome_options = options
        self.driver = self._create_driver()

    def _create_driver(self):
        """Initializes and returns a new WebDriver instance."""
        return webdriver.Chrome(options=self.chrome_options)

    def cycle_driver(self):
        """Closes the current driver and opens a new one."""

        # 1. Close the old driver instance
        if self.driver:
            try:
                self.driver.quit()
                print("Successfully closed old driver.")
            except Exception as e:
                # Handle cases where the driver might have crashed or timed out
                print(f"Warning: Could not quit old driver cleanly: {e}")

        # 2. Create and assign a new driver instance
        self.driver = self._create_driver()
        print("Successfully created new driver.")