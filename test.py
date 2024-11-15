import time
import os
import json
import const

def wait_for_response(timeout=60):
    response_file = "../linkedin-scrap-jobs-data/captcha_check.json"
    start_time = time.time()
    response = None
    while time.time() - start_time < timeout:
        if os.path.isfile(response_file):
            print("in")
            try:
                with open(response_file, "r") as f:
                    captcha_check_json = json.load(f)
                    if "img_name" in captcha_check_json:
                        response = captcha_check_json["img_name"]
            except Exception as e:
                print(f"Could not open captcha check json file {e}")
        time.sleep(1)
    with open(response_file, "w") as f:
        json.dump({}, f)
    return response  # Timeout if no response

wait_for_response()