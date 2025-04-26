from flask import Flask, request, render_template
from translator import translate_text

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    detected_language = ""
    english_text = ""
    back_translated_text = ""
    if request.method == 'POST':
        input_text = request.form.get('text', '')
        if input_text.strip():
            detected_language, english_text, back_translated_text = translate_text(input_text)
    return render_template('index.html', detected_language=detected_language, english_text=english_text, back_translated_text=back_translated_text)

if __name__ == '__main__':
    app.run(debug=True)



from flask import Flask, request, render_template
import os
from translator import translate_text, detect_language, text_to_speech, speech_to_text

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    audio_path = ""
    detected_language = ""
    english_text = ""
    back_translated_text = ""

    if request.method == 'POST':
        if 'file' in request.files:
            # Handle voice input (audio file upload)
            file = request.files['file']
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'input_audio.wav')
            file.save(filepath)

            # Step 1: Speech to Text
            recognized_text, detected_language_code = speech_to_text(filepath)
            detected_language = detected_language_code if detected_language_code else ""

            if recognized_text:  # Only proceed if text was recognized
                # Step 2: Translate to English
                english_text = translate_text(recognized_text)

                # Step 3: Translate back to original language
                back_translated_text = translate_text(english_text, to_lang=detected_language_code)

                # Step 4: Text to Speech (Original language)
                audio_path = text_to_speech(back_translated_text, detected_language_code)
            else:
                detected_language = ""
                english_text = "⚠️ No speech detected."
                back_translated_text = ""
                audio_path = ""

        elif 'text' in request.form:
            # Handle typed input
            input_text = request.form['text']
            if input_text.strip():
                # Step 1: Detect Language
                detected_language_code = detect_language(input_text)
                detected_language = detected_language_code if detected_language_code else ""

                # Step 2: Translate to English
                english_text = translate_text(input_text)

                # Step 3: Translate back to original language
                back_translated_text = translate_text(english_text, to_lang=detected_language_code)

                # Step 4: Text to Speech (Original language)
                audio_path = text_to_speech(back_translated_text, detected_language_code)

    return render_template('index.html',
                           audio_path=audio_path,
                           detected_language=detected_language,
                           english_text=english_text,
                           back_translated_text=back_translated_text)

if __name__ == '__main__':
    app.run(debug=True)


import os
import requests
import uuid
from flask import Flask, request, render_template
from translator import translate_text, detect_language, text_to_speech, speech_to_text

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Language code to name mapping (same as you already have)
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

@app.route('/', methods=['GET', 'POST'])
def index():
    detected_language = ""
    english_text = ""
    back_translated_text = ""
    audio_path = ""

    if request.method == 'POST':
        if 'file' in request.files:
            # Handle voice input (audio file upload)
            file = request.files['file']
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'input_audio.wav')
            file.save(filepath)

            # Step 1: Convert speech to text
            recognized_text, detected_language_code = speech_to_text(filepath)
            detected_language = language_map.get(detected_language_code, detected_language_code)

            if recognized_text:  # Process only if there's recognized text
                # Step 2: Translate to English
                english_text = translate_text(recognized_text)

                # Step 3: Translate back to original language
                back_translated_text = translate_text(english_text, to_lang=detected_language_code)

                # Step 4: Text to Speech (Back-translated text)
                audio_path = text_to_speech(back_translated_text, detected_language_code)
            else:
                detected_language = ""
                english_text = "No speech detected."
                back_translated_text = ""
                audio_path = ""
        
        elif 'text' in request.form:
            # Handle typed input (same as before)
            input_text = request.form['text']
            if input_text.strip():
                detected_language_code = detect_language(input_text)
                detected_language = language_map.get(detected_language_code, detected_language_code)
                english_text = translate_text(input_text)
                back_translated_text = translate_text(english_text, to_lang=detected_language_code)
                audio_path = text_to_speech(back_translated_text, detected_language_code)

    return render_template('index.html',
                           audio_path=audio_path,
                           detected_language=detected_language,
                           english_text=english_text,
                           back_translated_text=back_translated_text)

if __name__ == '__main__':
    app.run(debug=True)
