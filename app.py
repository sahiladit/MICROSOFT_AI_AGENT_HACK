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
