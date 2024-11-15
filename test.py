import google.generativeai as genai
import json

genai.configure(api_key="AIzaSyC6PdT-QJQ3X4m6Kp1UG3m5WZ8u-TzH2Do")

image_1 = genai.upload_file(path="../linkedin-scrap-jobs-data/page_html_4 (1).png", display_name="image_1")

# Choose a Gemini model.
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Prompt the model with text and the previously uploaded image.
response = model.generate_content(["Repond avec un json de format {'reponse': image_id} ou id sera le numéro de la case, dans l'ordre de 1 à 6 les cases partent de la case en haut à gauche pour finir à la case en bas en droite, la question est : Choisissez une case qui présente trois objets identiques, ignorez les couleurs se concentrer seulement sur les formes", image_1])

print(response.text)
