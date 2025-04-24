from flask import Flask, render_template, request, jsonify, send_from_directory
from transformers import pipeline
import requests
import os
from rembg import remove
from recognition import detectEnglish, detectTurkish
from changebacckround import change_background
from werkzeug.utils import secure_filename
from googletrans import Translator
import asyncio
import aiohttp

app = Flask(__name__)

UPLOAD_FOLDER1 = 'static/uploads'  
RESULT_FOLDER1 = 'static/results'  

os.makedirs(UPLOAD_FOLDER1, exist_ok=True)
os.makedirs(RESULT_FOLDER1, exist_ok=True)


app.config['UPLOAD_FOLDER1'] = UPLOAD_FOLDER1
app.config['RESULT_FOLDER1'] = RESULT_FOLDER1


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
    selected_language = request.form.get("hidden_language", "english")
    result = detectEnglish() if selected_language == "english" else detectTurkish()
    return render_template("speechtotext.html", language=selected_language, result=result)



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


@app.route("/learn")
def learn():
    return render_template("learnmore.html")


if __name__ == "__main__":
    app.run(debug=True)
