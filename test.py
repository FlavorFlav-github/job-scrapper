import google.generativeai as genai


genai.configure(api_key="AIzaSyC6PdT-QJQ3X4m6Kp1UG3m5WZ8u-TzH2Do")

image_1 = genai.upload_file(path="../linkedin-scrap-jobs/image_1.png", display_name="image_1")
image_2 = genai.upload_file(path="../linkedin-scrap-jobs/image_2.png", display_name="image_2")
image_3 = genai.upload_file(path="../linkedin-scrap-jobs/correct_image_captcha_3.png", display_name="image_3")
image_4 = genai.upload_file(path="../linkedin-scrap-jobs/image_4.png", display_name="image_4")
image_5 = genai.upload_file(path="../linkedin-scrap-jobs/image_5.png", display_name="image_5")

# Choose a Gemini model.
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Prompt the model with text and the previously uploaded image.
response = model.generate_content(["Give me the name of the well oriented image", image_1, image_2, image_3, image_4, image_5])

print(response.text)
