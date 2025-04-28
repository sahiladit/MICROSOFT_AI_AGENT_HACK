from flask import Flask, request, render_template
from translator import detect_and_translate_to_english, translate_back_to_original

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    detected_language = ""
    english_text = ""
    back_translated_text = ""
    
    if request.method == 'POST':
        input_text = request.form.get('text', '')
        if input_text.strip():
            detected_language, english_text, detected_lang_code = detect_and_translate_to_english(input_text)
            back_translated_text = translate_back_to_original(english_text, detected_lang_code)
    
    return render_template('index.html',
                           detected_language=detected_language,
                           english_text=english_text,
                           back_translated_text=back_translated_text)

if __name__ == '__main__':
    app.run(debug=True)
