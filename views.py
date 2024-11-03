from flask import render_template, request, redirect, url_for
from models import Jobs
import time
from azure.cognitiveservices.speech import SpeechRecognitionEventArgs
from processor import start_transcription, conver_to_wav, get_file_extension
import threading

from app import app, db

@app.route("/")
@app.route("/home")
def home():
    data = Jobs.query.all()
    return render_template("home.html", data=data)

@app.route("/new-job", methods=["POST"])
def new_job():
    data = request.form
    phrase_list = data["phraseList"].split(";")
    audio = request.files["file"]
    audio_path = f"uploads/{int(time.time())}_{audio.filename}"
    audio.save(audio_path)

    if get_file_extension(audio_path) != "wav":
        audio_path = conver_to_wav(audio_path, replace=True)
        print("######## REPLACE AUDIO | CHANE EXXTENSION", audio_path)
    
    text = ""
    job_data = Jobs(
        title=data["title"], 
        audio_path=audio_path,
        details=data["details"], 
        status="Processing", 
        phrases=data["phraseList"])
    db.session.add(job_data)
    db.session.commit()

    thread = threading.Thread(target=start_transcription, args=(audio_path, phrase_list, job_data.id))
    thread.start()

    return "Processing", 200

@app.route("/transcription/<string:uuid>")
def transcription(uuid):
    job_data = Jobs.query.filter_by(uuid=uuid).first()
    list_phrase = job_data.phrases.split(";")
    return render_template("transcription.html", data = job_data, list_phrase=list_phrase)
