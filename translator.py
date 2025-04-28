import requests
import uuid

# Language code to name mapping
language_map = {
    'hi': 'Hindi',
    'mr': 'Marathi',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ta': 'Tamil',
    'te': 'Telugu',
    'en': 'English',
    'bn': 'Bengali',
    'pa': 'Punjabi',
    'ml': 'Malayalam',
    'or': 'Odia',
    'as': 'Assamese',
    'ur': 'Urdu',
    'kok': 'Konkani',
    'mai': 'Maithili',
    'ks': 'Kashmiri',
    'ne': 'Nepali',
    'sd': 'Sindhi',
    'sa': 'Sanskrit',
    'bho': 'Bhojpuri',
    'dog': 'Dogri',
    'mni': 'Manipuri',
    'sat': 'Santali',
}

key = "7oOd359wYDvLZkGPy6rhbgCKBWmfiNDxbjnSHEEaxmGxgxIFCqY2JQQJ99BDACGhslBXJ3w3AAAbACOGsJTd"
endpoint = "https://api.cognitive.microsofttranslator.com/"
region = "centralindia"

headers = {
    'Ocp-Apim-Subscription-Key': key,
    'Ocp-Apim-Subscription-Region': region,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}


def detect_and_translate_to_english(text):
    # Step 1: Detect Language
    detect_url = f"{endpoint.rstrip('/')}/detect?api-version=3.0"
    body = [{'Text': text}]
    detect_response = requests.post(detect_url, headers=headers, json=body)
    detect_response.raise_for_status()
    detected_lang = detect_response.json()[0]['language']
    detected_language_name = language_map.get(detected_lang, detected_lang)
    print(f"🕵️ Detected Language: {detected_lang} ({detected_language_name})")

    # Step 2: Translate to English
    translate_to_english_url = f"{endpoint.rstrip('/')}/translate?api-version=3.0&from={detected_lang}&to=en"
    translate_response = requests.post(translate_to_english_url, headers=headers, json=body)
    translate_response.raise_for_status()
    english_text = translate_response.json()[0]['translations'][0]['text']
    print("🔠 Translated to English:", english_text)

    return detected_language_name, english_text, detected_lang   # notice: returning 3 values


def translate_back_to_original(english_text, original_lang_code):
    body_back = [{'Text': english_text}]
    translate_back_url = f"{endpoint.rstrip('/')}/translate?api-version=3.0&from=en&to={original_lang_code}"
    translate_back_response = requests.post(translate_back_url, headers=headers, json=body_back)
    translate_back_response.raise_for_status()
    back_translated_text = translate_back_response.json()[0]['translations'][0]['text']
    print("🔁 Back-Translated to Original:", back_translated_text)

    return back_translated_text
