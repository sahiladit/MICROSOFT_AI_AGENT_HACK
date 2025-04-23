import requests, os

def translate(text, to_lang="en"):
    endpoint = "https://api.cognitive.microsofttranslator.com/translate"
    headers = {
        'Ocp-Apim-Subscription-Key': os.getenv("AZURE_TRANSLATOR_KEY"),
        'Ocp-Apim-Subscription-Region': os.getenv("AZURE_TRANSLATOR_REGION"),
        'Content-type': 'application/json'
    }
    params = {'api-version': '3.0', 'to': to_lang}
    body = [{'text': text}]
    response = requests.post(endpoint, params=params, headers=headers, json=body)
    return response.json()[0]['translations'][0]['text']