import google.generativeai as genai
import json

genai.configure(api_key="AIzaSyC6PdT-QJQ3X4m6Kp1UG3m5WZ8u-TzH2Do")

image_1 = genai.upload_file(path="../linkedin-scrap-jobs/image_1.png", display_name="image_1")
image_2 = genai.upload_file(path="../linkedin-scrap-jobs/image_2.png", display_name="image_2")
image_3 = genai.upload_file(path="../linkedin-scrap-jobs/correct_image_captcha_3.png", display_name="image_3")
image_4 = genai.upload_file(path="../linkedin-scrap-jobs/image_4.png", display_name="image_4")
image_5 = genai.upload_file(path="../linkedin-scrap-jobs/image_5.png", display_name="image_5")

# Choose a Gemini model.
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Prompt the model with text and the previously uploaded image.
response = model.generate_content(["I want the response to be a json in the format {'image_1': true, 'image_2': true, 'image_3': true, 'image_4': true, 'image_5': true, 'image_6': true} Attribute the value true only to the image that responds the best to the following question : Which image is well oriented", image_1, image_2, image_3, image_4, image_5])

print(json.loads(response.text.replace("```", "").replace("json", "").replace("'", '"')))
