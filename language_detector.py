from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load tokenizer and model
model_name = "papluca/xlm-roberta-base-language-detection"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


# Define the language detection function
def detect_language_transformers(text):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    confidences, indices = torch.max(predictions, dim=1)

    # Get the language label and confidence score
    lang_code = model.config.id2label[indices.item()]
    confidence = confidences.item()
    return lang_code, confidence
