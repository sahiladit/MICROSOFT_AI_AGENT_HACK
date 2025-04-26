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


def translate_text(text):
    key = "7oOd359wYDvLZkGPy6rhbgCKBWmfiNDxbjnSHEEaxmGxgxIFCqY2JQQJ99BDACGhslBXJ3w3AAAbACOGsJTd"
    endpoint = "https://api.cognitive.microsofttranslator.com/"
    region = "centralindia"

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

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

    # Step 3: Translate back to original language
    body_back = [{'Text': english_text}]
    translate_back_url = f"{endpoint.rstrip('/')}/translate?api-version=3.0&from=en&to={detected_lang}"
    translate_back_response = requests.post(translate_back_url, headers=headers, json=body_back)
    translate_back_response.raise_for_status()
    back_translated_text = translate_back_response.json()[0]['translations'][0]['text']
    print("🔁 Back-Translated to Original:", back_translated_text)

    return detected_language_name, english_text, back_translated_text



import requests
import uuid
import os

# Language mappings
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

voice_map = {
    'hi': 'hi-IN-SwaraNeural',
    'mr': 'mr-IN-AarohiNeural',
    'gu': 'gu-IN-DhwaniNeural',
    'kn': 'kn-IN-GaganNeural',
    'ta': 'ta-IN-PallaviNeural',
    'te': 'te-IN-MohanNeural',
    'bn': 'bn-IN-TanishaaNeural',
    'pa': 'pa-IN-AvneetNeural',
    'ml': 'ml-IN-MidhunNeural',
    'or': 'or-IN-PrabhatNeural',
    'as': 'as-IN-ParthNeural',
    'ur': 'ur-IN-AsadNeural',
    'en': 'en-IN-NeerjaNeural',
}

# Azure Keys (replace with your real keys)
TRANSLATOR_KEY = "7oOd359wYDvLZkGPy6rhbgCKBWmfiNDxbjnSHEEaxmGxgxIFCqY2JQQJ99BDACGhslBXJ3w3AAAbACOGsJTd"
SPEECH_KEY = "EJGgAIRRVfgyjJKm5Q7LM7r4Mq7RZ7tnAKbz5XKGMKGI8yDzo7MSJQQJ99BDACGhslBXJ3w3AAAYACOGKRms"
REGION = "centralindia"

# Detect language from text
def detect_language(text):
    endpoint = "https://api.cognitive.microsofttranslator.com/"
    headers = {
        'Ocp-Apim-Subscription-Key': TRANSLATOR_KEY,
        'Ocp-Apim-Subscription-Region': REGION,
        'Content-type': 'application/json',
    }
    body = [{'Text': text}]
    response = requests.post(endpoint, headers=headers, json=body)
    response.raise_for_status()
    detected_lang = response.json()[0]['language']
    return detected_lang

# Translate text
def translate_text(text, to_lang='en'):
    if not text.strip():  # 🚨 early exit if text is empty
        return ""
    endpoint = f"https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to={to_lang}"
    headers = {
        'Ocp-Apim-Subscription-Key': TRANSLATOR_KEY,
        'Ocp-Apim-Subscription-Region': REGION,
        'Content-type': 'application/json',
    }
    body = [{'Text': text}]
    response = requests.post(endpoint, headers=headers, json=body)
    response.raise_for_status()
    translated_text = response.json()[0]['translations'][0]['text']
    return translated_text

# Text to Speech
def text_to_speech(text, lang_code):
    speech_endpoint = "https://centralindia.api.cognitive.microsoft.com/"
    voice = voice_map.get(lang_code, 'en-IN-NeerjaNeural')

    headers = {
        'Ocp-Apim-Subscription-Key': SPEECH_KEY,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-32kbitrate-mono-mp3',
        'User-Agent': 'AzureTTSApp'
    }

    ssml = f"""
    <speak version='1.0' xml:lang='{lang_code}'>
        <voice xml:lang='{lang_code}' name='{voice}'>
            {text}
        </voice>
    </speak>
    """

    response = requests.post(speech_endpoint, headers=headers, data=ssml.encode('utf-8'))
    response.raise_for_status()

    audio_file = f'static/output_{uuid.uuid4()}.mp3'
    os.makedirs('static', exist_ok=True)
    with open(audio_file, 'wb') as f:
        f.write(response.content)

    print(f"🔊 TTS saved at: {audio_file}")
    return audio_file

# Speech to Text
def speech_to_text(audio_file_path):
    endpoint = f"https://{REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    params = {
        'language': 'en-IN'  # or auto-detect later
    }
    headers = {
        'Ocp-Apim-Subscription-Key': SPEECH_KEY,
        'Content-Type': 'audio/wav',
    }

    with open(audio_file_path, 'rb') as audio_file:
        response = requests.post(endpoint, params=params, headers=headers, data=audio_file)
    response.raise_for_status()

    result = response.json()
    print("🎙 Recognized:", result)

    text = result.get('DisplayText', '')
    if not text.strip():
        return None, None  # <- important change!

    # Language detection based on text
    detected_language_code = detect_language(text)
    return text, detected_language_code



import requests
import json
import time

# Function to get an access token using the Azure Speech API subscription key
def get_access_token(subscription_key, region):
    url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print("Error fetching access token")
        print(response.status_code, response.text)
        return None

# Function to recognize speech using Azure REST API
def speech_to_text(endpoint, audio_path, subscription_key, region):
    token = get_access_token(subscription_key, region)
    if not token:
        return "", ""

    # Set the correct endpoint for speech-to-text
    url = f"https://{region}.api.cognitive.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"

    headers = {
        'Content-Type': 'audio/wav',  # or use audio/mpeg for MP3 files
        'Authorization': f'Bearer {token}',
        'Ocp-Apim-Subscription-Key': subscription_key
    }

    with open(audio_path, 'rb') as audio_file:
        audio_data = audio_file.read()

    response = requests.post(url, headers=headers, data=audio_data)

    if response.status_code == 200:
        # Parse the response
        result = response.json()
        recognized_text = result.get('DisplayText', '')
        detected_language_code = result.get('Language', '')

        print("Recognized Speech:", recognized_text)
        print(f"Detected Language: {detected_language_code}")

        return recognized_text, detected_language_code
    else:
        print("Speech recognition failed:", response.status_code, response.text)
        return "", ""

# Example usage
subscription_key = "EJGgAIRRVfgyjJKm5Q7LM7r4Mq7RZ7tnAKbz5XKGMKGI8yDzo7MSJQQJ99BDACGhslBXJ3w3AAAYACOGKRms"
region = "centralindia"
audio_path = "static/input_audio.wav"  # Path to the audio file

# Call the function with the correct endpoint
recognized_text, detected_language_code = speech_to_text(f"https://{region}.api.cognitive.microsoft.com/", audio_path, subscription_key, region)
print("Recognized Text:", recognized_text)
print("Detected Language:", detected_language_code)
