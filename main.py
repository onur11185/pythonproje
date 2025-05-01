from flask import Flask, render_template, request, jsonify, send_from_directory, session
from transformers import pipeline
import requests
import os
from rembg import remove
from recognition import detectEnglish, detectTurkish, detectGerman, detectFrench, detectItalian, detectSpanish
from changebacckround import change_background
from werkzeug.utils import secure_filename
from googletrans import Translator
import asyncio
import aiohttp
import string
import openai
import language_tool_python 
from collections import Counter
import re

app = Flask(__name__)

UPLOAD_FOLDER1 = 'static/uploads'  
RESULT_FOLDER1 = 'static/results'  

os.makedirs(UPLOAD_FOLDER1, exist_ok=True)
os.makedirs(RESULT_FOLDER1, exist_ok=True)


app.config['UPLOAD_FOLDER1'] = UPLOAD_FOLDER1
app.config['RESULT_FOLDER1'] = RESULT_FOLDER1


openai.api_key = ''



async def translate_async(text, source_language, target_language):
    async with aiohttp.ClientSession() as session:
        url = f'https://api.mymemory.translated.net/get?q={text}&langpair={source_language}|{target_language}'
        async with session.get(url) as response:
            data = await response.json()
            return data['responseData']['translatedText']  


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/summarize", methods=["GET", "POST"])
def summarize():
    summary = ""
    if request.method == "POST":
        user_input = request.form["text"]
        summarizer = pipeline("summarization")
        result = summarizer(user_input, max_length=130, min_length=30, do_sample=False)
        summary = result[0]['summary_text']
    return render_template("summarize.html", summary=summary)


@app.route("/speechtotext")
def speechtotext():
    return render_template("speechtotext.html")


@app.route("/speechtotextt", methods=["POST"])
def speechtotexttt():
    language_detect_function = {
        "english": detectEnglish,
        "turkish": detectTurkish,
        "german": detectGerman,
        "spanish": detectSpanish,
        "french": detectFrench,
        "italian": detectItalian
    }

    selected_language = request.form.get("language", "english")

    result = language_detect_function.get(selected_language, lambda: "Language not supported.")()

    return render_template("speechtotext.html", language=selected_language, result=result)


@app.route('/texttospeech')
def text_to_speech():
    return render_template('texttospeech.html')


@app.route("/changebackround", methods=["GET", "POST"])
def changebackround():
    result_image = None
    error_message = None

    if request.method == "POST":
        try:
            image = request.files['image']
            background = request.files['background']

            if image and background:
                image_filename = secure_filename(image.filename)
                background_filename = secure_filename(background.filename)

                image_path = os.path.join(app.config['UPLOAD_FOLDER1'], image_filename)
                background_path = os.path.join(app.config['UPLOAD_FOLDER1'], background_filename)

                image.save(image_path)
                background.save(background_path)

                result_filename = 'replaced_' + image_filename
                result_path = os.path.join('static/results', result_filename)

                change_background(background_path, image_path, result_path)

                result_image = result_filename

        except Exception as e:
            error_message = str(e)

    return render_template("changebackround.html", result_image=result_image, error=error_message)



@app.route("/deletebackround", methods=["GET", "POST"])
def deletebackround():
    result_image = None
    if request.method == "POST":
        image = request.files['image']
        upload_folder = UPLOAD_FOLDER1 if request.form.get("folder_choice") == "1" else UPLOAD_FOLDER1
        if image:
            input_path = os.path.join(upload_folder, image.filename)
            image.save(input_path)

            output_folder = RESULT_FOLDER1 if request.form.get("folder_choice") == "1" else RESULT_FOLDER1
            output_path = os.path.join(output_folder, f"processed_{image.filename}")
            with open(input_path, 'rb') as i:
                input_data = i.read()
                output_data = remove(input_data)
                with open(output_path, 'wb') as o:
                    o.write(output_data)

            result_image = f"processed_{image.filename}"

    return render_template("deletebackround.html", result_image=result_image)


@app.route('/translate', methods=['GET', 'POST'])
def translate():
    if request.method == 'POST':
        source_language = request.form['source_language']
        target_language = request.form['target_language']
        source_text = request.form['source_text']
        
        translated_text = translate_sync(source_text, source_language, target_language)
        
        return render_template('translate.html', 
                               source_language=source_language, 
                               target_language=target_language, 
                               translated_text=translated_text)
    
    return render_template('translate.html')


def translate_sync(text, source_language, target_language):
    url = f'https://api.mymemory.translated.net/get?q={text}&langpair={source_language}|{target_language}'
    response = requests.get(url)
    data = response.json()
    return data['responseData']['translatedText']



@app.route("/analyzer", methods=["GET", "POST"])
def analyze_text():
    if request.method == "POST":
        text = request.form["text"]

        word_count = len(text.split())

        sentence_count = text.count('.') + text.count('!') + text.count('?')


        sentences = text.split('.')
        total_words = sum(len(sentence.split()) for sentence in sentences)
        avg_sentence_length = total_words / len(sentences) if len(sentences) > 0 else 0

        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        words = text.split()

        stopwords = set(["the", "and", "a", "to", "of", "in", "on", "for", "with", "that", "this", "is", "it"])
        words = [word for word in words if word not in stopwords]
        most_common = Counter(words).most_common(5)

        most_used_words = [word for word, _ in most_common]

        return render_template("textanalyzer.html", 
                               word_count=word_count, 
                               sentence_count=sentence_count, 
                               avg_sentence_length=avg_sentence_length, 
                               most_used_words=most_used_words)
    
    return render_template("textanalyzer.html")  




@app.route("/learn")
def learn():
    return render_template("learnmore.html")




@app.route('/grammar', methods=['GET', 'POST'])
def grammar():
    if request.method == 'POST':
        user_text = request.form['text']
        corrected_text = user_text
        num_issues = 0
        detected_issues_names = []

        try:
            prompt = f"Correct the grammar, punctuation, and structure of the following sentence:\n\n{user_text}"
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a grammar correction assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            corrected_text = response['choices'][0]['message']['content'].strip()
            detected_issues_names.append("Corrected using GPT-3.5 Turbo")

        except Exception as e:
            try:
                tool = language_tool_python.LanguageTool('en-US')
                matches = tool.check(user_text)
                corrected_text = language_tool_python.utils.correct(user_text, matches)
                num_issues = len(matches)
                detected_issues_names = list(set(match.ruleIssueType for match in matches))
                detected_issues_names.insert(0, "Corrected using LanguageTool")

            except Exception as fallback_error:
                corrected_text = f"Both correction methods failed: {str(fallback_error)}"

        return render_template('grammar.html',
                               result=corrected_text,
                               text=user_text,
                               num_issues=num_issues,
                               detected_issues=detected_issues_names)

    return render_template('grammar.html')






@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        language_preference = request.form.get("language_preference")
        theme_preference = request.form.get("theme_preference")
        
        session['language_preference'] = language_preference
        session['theme_preference'] = theme_preference

        return render_template("settings.html", saved=True)
    
    return render_template("settings.html")


if __name__ == "__main__":
    app.run(debug=True)
