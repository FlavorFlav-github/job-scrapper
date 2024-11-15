import requests
from selenium import webdriver
from PIL import Image
from io import BytesIO
import cv2
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from skimage .metrics import structural_similarity as ssim
from telegram import Bot
import asyncio
import telegramHook
import google.generativeai as genai
import jobs_read_write
import datetime
import check_new_added_jobs
import time
import json
import const
import math


# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument("--disable-gpu")  # (optional) To avoid some issues on Windows
chrome_options.add_argument("--no-sandbox")  # (optional) Useful for running in Docker
chrome_options.add_argument("--disable-dev-shm-usage")  # (optional) To avoid some memory issues

# Set up logging preferences directly in Chrome options
chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

# Run the chrome driver (launches the web browser)
driver = webdriver.Chrome(options=chrome_options)


def screenshot_page(id_screen):
    # Take a screenshot of the element
    img_png = driver.find_element(By.TAG_NAME, "body").screenshot_as_png
    img_name = f"../linkedin-scrap-jobs-data/page_html_{id_screen}.png"
    # Open the image in PIL and save it as PNG
    img = Image.open(BytesIO(img_png))
    img.save(img_name)


# Function to capture API requests and responses
def get_headers(url, template):
    print("Start to get cookies")
    # Enable network tracking with CDP
    driver.execute_cdp_cmd("Network.enable", {})
    driver.get(url)
    time.sleep(3)
    logs = driver.get_log("performance")
    # Search linkedin mandatory cookies
    cookies = driver.get_cookies()
    const.linkedin_cookie = ""
    csrf_token = ""
    request_out = None
    for cookie in cookies:
        if cookie['name'] in ["li_at", "JSESSIONID", "lang", "li_mc", "li_gc", "lidc", "bcookie", "bscookie"]:
            const.linkedin_cookie += f'{cookie["name"]}={cookie["value"]};'
    for entry in logs:
        try:
            message = json.loads(entry["message"])["message"]
            if message["method"] == "Network.requestWillBeSent":
                network_request = message["params"]["request"]
                if template in network_request["url"]:
                    headers = network_request.get("headers")
                    headers["cookie"] = const.linkedin_cookie
                    request_out = {
                        "headers": headers
                    }
                    break
        except Exception as e:
            continue

    if len(const.linkedin_cookie) > 0:
        print("Cookies get successfully")
    else:
        print("Cookies not found")

    # Disable network tracking once done
    driver.execute_cdp_cmd("Network.disable", {})
    return request_out


def check_captcha():
    def resolve_captcha_v3():
        # Save the screen as png
        img_png = driver.find_element(By.TAG_NAME, "body").screenshot_as_png
        img_name = f"../linkedin-scrap-jobs-data/page_html.png"

        # Open the image in PIL and save it as PNG
        img = Image.open(BytesIO(img_png))
        img.save(img_name)

        # Fetch the cases
        image_list = driver.find_element(By.TAG_NAME, "ul").find_elements(By.TAG_NAME, "li")
        images = {}
        for img in image_list:
            img_id = img.get_attribute('id')
            print(f"Fetching image with id {img.get_attribute('id')}")
            image_represented = img.find_element(By.TAG_NAME, "a")
            images[img_id] = image_represented

        # Send the picture to telegram
        bot = Bot(token=const.telegrambottoken)
        asyncio.run(bot.send_photo(chat_id=const.telegrambotchatid, photo=img_name))

        # Wait or the response
        telegramHook.start_bot_thread()
        response = telegramHook.wait_for_response()
        if response is not None:
            # Identify the case to click on
            if response in images:
                # Click the case
                images[response].click()

    def resolve_captcha_v2():
        # Instantiate Gemini API
        genai.configure(api_key=const.gemini_api_key)

        # Upload images to genai
        image_list = driver.find_element(By.TAG_NAME, "ul").find_elements(By.TAG_NAME, "li")
        images = []
        images_id_array = []
        json_structure_for_prompt = {}
        # Create an ActionChains object
        actions = ActionChains(driver)
        for img in image_list:
            img_id = img.get_attribute('id')
            print(f"Fetching image with id {img.get_attribute('id')}")
            image_represented = img.find_element(By.TAG_NAME, "a")
            # Move the cursor to the element and hover
            actions.move_to_element(image_represented).perform()
            time.sleep(1)
            img_png = image_represented.screenshot_as_png
            img_name = f"../linkedin-scrap-jobs-data/{img_id}.png"
            # Open the image in PIL and save it as PNG
            img = Image.open(BytesIO(img_png))
            img.save(img_name)
            image_gen_ai = genai.upload_file(path=img_name, display_name=img_id)
            images_id_array.append(image_gen_ai)
            json_structure_for_prompt[img_id] = True
            images.append({"image_name": img_id, "image_link": img_name, "gen_ai_img": image_gen_ai,
                           "driver_element": image_represented})

        # Get the text to ask the ai
        text_gan_ai = driver.find_element(By.ID, "game_children_text").find_element(By.TAG_NAME, "h2").text
        print(f"Question to ask : {text_gan_ai}")

        # Send text request to genai to get gthe correct image to click on
        # Choose a Gemini model.
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        prompt_content = [
                             f"I want the response to be a json in the format {json.dumps(json_structure_for_prompt)} Attribute the value true only to the image that responds the best to the following question : {text_gan_ai}, Ne pas tenir comptes des couleurs, seulement des formes"] + images_id_array
        # Prompt the model with text and the previously uploaded image.
        response = model.generate_content(prompt_content)
        # Convert the response to json
        json_response = json.loads(response.text.replace("```", "").replace("json", "").replace("'", '"'))
        print(f'Gemini response : {json_response}')
        # Click the image to resolve the captcha
        for img in images:
            if img["image_name"] in json_response and json_response[img["image_name"]]:
                img["driver_element"].click()
                print(f"Clicked on the image {img['image_name']}")
                break
    def resolve_captcha():
        images = []
        print(driver.page_source)
        # Load the images
        for i in range(6):
            id=i+1
            # Locate the image element
            img_element = driver.find_element(By.ID, f"image{id}").find_element(By.TAG_NAME, "a")

            # Take a screenshot of the element
            img_png = img_element.screenshot_as_png
            img_name = f"../linkedin-scrap-jobs-data/image_{id}.png"
            # Open the image in PIL and save it as PNG
            img = Image.open(BytesIO(img_png))
            img.save(img_name)
            images.append(img_name)
        # Load the correct image
        templates = ['../linkedin-scrap-jobs-data/correct_image_captcha_2.png',
                     '../linkedin-scrap-jobs-data/correct_image_captcha_3.png']
        results = []
        for template_url in templates:
            template = cv2.imread(template_url, cv2.IMREAD_GRAYSCALE)
            for image_path in images:
                image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

                # Resize or preprocess if necessary
                image = cv2.resize(image, (template.shape[1], template.shape[0]))

                # Edge detection using Canny to focus on shape
                edges1 = cv2.Canny(template, 100, 200)
                edges2 = cv2.Canny(image, 100, 200)

                # Compute SSIM between the two edge-detected images
                score, _ = ssim(edges1, edges2, full=True)

                # Convert score to percentage
                resemblance_percentage = score * 100

                # Add result to list, threshold based on similarity score
                results.append((image_path, resemblance_percentage))

        # Find the image with the highest match score (closest orientation)
        correct_image = max(results, key=lambda x: x[1])[0]
        print(correct_image)
        return correct_image

    print("Start to check page for captcha")
    check_captcha_length = len(driver.find_elements(By.ID, "captcha-internal"))
    loop_time = 0
    success = True
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    while check_captcha_length > 0:
        screenshot_page(loop_time)
        print("Captcha found, start resolving captcha")
        iframe_1 = driver.find_element(By.ID, "captcha-internal")
        driver.switch_to.frame(iframe_1)

        iframe_2 = driver.find_element(By.ID, "arkoseframe")
        driver.switch_to.frame(iframe_2)

        iframe_3 = driver.find_element(By.CSS_SELECTOR, 'iframe[title="Verification challenge"]')
        driver.switch_to.frame(iframe_3)

        iframe_4 = driver.find_element(By.ID, "fc-iframe-wrap")
        driver.switch_to.frame(iframe_4)

        iframe_5 = driver.find_element(By.ID, "CaptchaFrame")
        driver.switch_to.frame(iframe_5)

        try:
            verify_button = driver.find_element(By.XPATH, '//button[text()="Vérifier"]')
            verify_button.click()
        except Exception:
            pass
        time.sleep(2)

        resolve_captcha_v3()
        time.sleep(3)
        driver.switch_to.default_content()
        loop_time += 1
        if loop_time == 8:
            success = False
            break
        else:
            check_captcha_length = len(driver.find_elements(By.ID, "captcha-internal"))
    print("Check for captcha terminated")
    return success


def get_jobs(url, headers, count, start):
    url += f"&start={start}&count={count}"
    response = requests.get(url, headers=headers)
    print(f"[{response.status_code}] - {url}")
    if response.status_code == 200:
        return response.json()
    else:
        print(response.content.decode())
        return None


def get_job_detail(job_id, headers):
    url = f"https://www.linkedin.com/voyager/api/jobs/jobPostings/{job_id}?decorationId=com.linkedin.voyager.deco.jobs.web.shared.WebFullJobPosting-65&topN=1&topNRequestedFlavors=List(TOP_APPLICANT,IN_NETWORK,COMPANY_RECRUIT,SCHOOL_RECRUIT,HIDDEN_GEM,ACTIVELY_HIRING_COMPANY)"
    response = requests.get(url, headers=headers)
    print(f"[{response.status_code}] - {url}")
    if response.status_code == 200:
        return response.json()
    else:
        print(response.content.decode())
        return None


def main_scrap_linkedin():
    # Connect to the application using email and passwords input
    driver.get("https://www.linkedin.com/login/fr?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")

    # Fill the username field
    username_element = driver.find_element(By.ID, "username")
    time.sleep(1)
    username_element.send_keys(const.linkedin_username)

    # Fill the password field
    password_element = driver.find_element(By.ID, "password")
    time.sleep(1)
    password_element.send_keys(const.linkedin_password)

    # CLick the submit button to initiate the log in
    submit = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    time.sleep(1)
    submit.click()

    # Check the page for a captcha
    time.sleep(5)
    success = check_captcha()
    if success:
        # Wait until it is redirected to the main page of linkedin
        WebDriverWait(driver, 300).until(EC.url_contains("linkedin.com/feed"))
        for job_options in const.linkedin_search_parameter:
            geo_id = job_options["geo_id"]
            key_word = job_options["key_word"]

            # Get the request for listing jobs
            api_requests_responses = get_headers(f"https://www.linkedin.com/jobs/search?distance=25&geoId={geo_id}&keywords={key_word}&origin=JOBS_HOME_SEARCH_CARDS&start=125", "JobSearchCardsCollection-215")
            if api_requests_responses is not None:
                # Remove count and start uri parameter from url
                list_job_base_url = f"https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-215&q=jobSearch&query=(origin:JOBS_HOME_SEARCH_CARDS,keywords:{key_word},locationUnion:(geoId:{geo_id}),selectedFilters:(distance:List(25)),spellCorrectionEnabled:true)"
                linkedin_headers = api_requests_responses["headers"]

                # Get the max count of jobs to get from the API
                response_json = get_jobs(list_job_base_url, linkedin_headers, count=1, start=0)

                if response_json is not None:
                    max_jobs = response_json["data"]["paging"]["total"]
                    count = 50
                    linkedin_jobs_loaded = jobs_read_write.read_linkedin_jobs()
                    for i in range(math.ceil(max_jobs/count)):
                        start_point = count*i
                        count_point = min(count, max_jobs-start_point)
                        # Fetch jobs 50 elements at a time
                        response_json = get_jobs(list_job_base_url, linkedin_headers, count=count_point, start=start_point)
                        if response_json is not None:
                            jobs = response_json["included"]
                            jobs = [job for job in jobs if "jobPostingUrn" in job]
                            for job in jobs:
                                published_date = datetime.datetime.fromtimestamp([row for row in job["footerItems"] if "timeAt" in row][0]["timeAt"] / 1000).strftime('%Y-%m-%dT%H:%M:%S.%f')
                                job_id = job["jobPostingUrn"].split(":")[-1]
                                job_to_save = {"job_id": job_id,
                                               "job_title": job["jobPostingTitle"],
                                               "job_published_date": published_date,
                                               "job_employer": job["primaryDescription"]["text"],
                                               "job_city": job["secondaryDescription"]["text"],
                                               "job_url": f"https://www.linkedin.com/jobs/search/?currentJobId={job_id}",
                                               "job_origin": "Linkedin"}

                                # Check for duplicates in saved jobs
                                duplicates = False
                                for saved_job in linkedin_jobs_loaded:
                                    if saved_job["job_id"] == job_to_save["job_id"]:
                                        duplicates = True
                                        break
                                if not duplicates:
                                    job_detail = get_job_detail(job_to_save["job_id"], headers=linkedin_headers)
                                    job_to_save["job_description"] = job_detail["data"]["description"]["text"]
                                    job_to_save["job_industry"] = job_detail["data"]["formattedIndustries"]
                                    job_to_save["job_function"] = job_detail["data"]["formattedJobFunctions"]
                                    job_to_save["job_location"] = job_detail["data"]["formattedLocation"]
                                    job_to_save["job_level"] = job_detail["data"]["formattedExperienceLevel"]
                                    job_to_save["job_employment_status"] = job_detail["data"]["formattedEmploymentStatus"]
                                    linkedin_jobs_loaded.append(job_to_save)
                            with open(const.linkedin_jobs_output_file_link, "w") as f:
                                json.dump(linkedin_jobs_loaded, f)
        # Send the newly added jobs
        check_new_added_jobs.send_new_added_jobs(linkedin_jobs_loaded, const.new_jobs_lookback)
    else:
        print("Captcha was not resoled successfully")
    # Close the browser
    driver.quit()


if __name__ == '__main__':
    main_scrap_linkedin()
