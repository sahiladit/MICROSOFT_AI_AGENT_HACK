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
