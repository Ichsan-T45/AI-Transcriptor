import azure.cognitiveservices.speech as speechsdk
from google.generativeai.generative_models import GenerativeModel
import google.generativeai as genai
from flask_sqlalchemy import SQLAlchemy
from models import Jobs
from functools import partial
from app import app, db
import os

# Konfigurasi Azure Speech Service
speech_key = os.getenv("SPEECH_KEY")
service_region = os.getenv("SPEECH_REGION")
genai.configure(api_key=os.getenv("GEMINI_API="))

generation_config = {
    "temperature": 0.2,
    "top_p": 0.9,
    "response_mime_type": "text/plain",
    }

AUDIO_EXTENSIONS = [
    "aiff",
    "flac",
    "m4a",
    "mp3",
    "mp4",
    "wav",
    "ogg",
]


def start_transcription(audio_path, phrase_list:list, job_id: Jobs):
    print("connecting with : ",speech_key, " on: ", service_region)
    print("HERE's THE FIRST DATA >>>>> ", db.session)
    # service_region = os.getenv("SPEECH_REGION")
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_recognition_language = "id-ID" 
    audio_input = speechsdk.AudioConfig(filename=audio_path)  # Atau gunakan `AudioConfig(use_default_microphone=True)` untuk mikrofon

    # Inisialisasi recognizer   
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    if phrase_list:
        phrase_list_grammar = speechsdk.PhraseListGrammar(speech_recognizer) 

        for phrase in phrase_list:
            phrase_list_grammar.addPhrase(phrase=phrase)  

    
    def recog_cb(event):
        with app.app_context() as context:
            job_data =  db.session.query(Jobs).get(job_id)
            job_data.text_raw += "\n"+event.result.text
            db.session.commit()
            print(">>??????:", event.result.text)
            print("\n###??????:", job_data.title)

    # Menambahkan event handler untuk pengenalan suara berkelanjutan
    speech_recognizer.recognized.connect(recog_cb)

    def recog_end_cb(event):
        with app.app_context():
            print("Recognition Finished")
            job_data = db.session.query(Jobs).get(job_id)
            job_data.status="Done"
            
            # Fix transcription with Gemini API
            transcript = ai_formatting(job_data.text_raw)
            job_data.formatted = transcript
            
            transcript = ai_insert_questions(transcript, job_data.question_list)
            transcript = ai_spellcheck(transcript, job_data.details)
            
            job_data.text_ai = transcript
            
            db.session.commit()
            speech_recognizer.stop_continuous_recognition_async()
            try:
                os.remove(audio_path)
            except: pass
            
    # Menghentikan pengenalan suara kontinu
    speech_recognizer.speech_end_detected.connect(recog_end_cb)
    speech_recognizer.canceled.connect(lambda: print("<<<<< Canceled >>>>>"))
    speech_recognizer.session_stopped.connect(lambda: print("<<<<< Stopped >>>>>"))

    # Memulai pengenalan suara kontinu secara asinkron
    speech_recognizer.start_continuous_recognition_async()
    print ("\nSTARTING RECOGNITION JOB : ")
    # print ("STARTING RECOGNITION JOB : ")

def ai_formatting(transcript_raw):
    system_instruction = f"""
    Ubah script wawancara ke dalam format HTML. Pisahkan bagian Interviewer dan Narasumber. Berikan efek bold pada nama keduanya menggunakan tag span. Contoh script Output yang diharapkan: '<p><b>Interviewer:</b> Bagaimana pendapat Anda tentang... <p><b>Narasumber:</b> Saya pikir...'. 
    Pastikan poin berikut:
    1. Tidak ada teks/saran/informasi tambahan selain text transkrip yang telah di format.
    2. Abaikan tag tingkat atas seperty tag html, head dan body.
    """
    model = GenerativeModel(  
                                model_name="gemini-1.5-pro",
                                generation_config=generation_config,
                                system_instruction=system_instruction)
    
    
    formatted = model.generate_content(transcript_raw).text

    return formatted

def ai_insert_questions(transcript, questions):
    system_instruction = f"""
    Berikut merupakan transkrip wawancara dengan list pertanyaan sebagai berikut: ### {questions} ###. Ubahlah pertanyaan Interviewer yang ada di transkrip agar sesuai dengan list pertanyaan. 
    Pastikan poin berikut: 
    1. Tidak ada teks/saran/informasi tambahan selain text transkrip yang telah disunting.
    2. Tidak ada teks narasumber yang disunting dari teks input"""
    
    model = GenerativeModel(  
                                model_name="gemini-1.5-pro",
                                generation_config=generation_config,
                                system_instruction=system_instruction)
    result = model.generate_content(transcript).text
    return result

def ai_spellcheck(transcript, details):
    system_instruction = f"""
    Sunting transkrip wawancara yang di input dengan detail: ###{details} ###. Analisis lalu lakukan perbaikan kata yang salah transkrip kemudian bungkus dengan atribut span html dengan style berwarna hijau. Hapus semua kata pengisi atau filler yang berlebihan seperti uh, ehh, hmm, dan sejenisnya.
    Pastikan poin berikut: 
    1. Tidak ada teks/saran/informasi tambahan selain hasil suntingan teks input.
    2. Hilangkan
    """
    model = GenerativeModel(  
                                model_name="gemini-1.5-pro",
                                generation_config=generation_config,
                                system_instruction=system_instruction)
    result = model.generate_content(transcript).text
    return result


    
     

from pydub import AudioSegment
def conver_to_wav(audio_input: str, output: str = None, replace=False) -> str: 
    """convert audio to .wav
    expected input extension: .aif | .flac | .m4a | .mp3 | .mp4 | .ogg
    
    Args:
        path (str): audio path

    Returns:
        str: result's path
    """
    input_extension = get_file_extension(audio_input)
    if not input_extension in AUDIO_EXTENSIONS :
        raise TypeError(f"invalid audio input extension : {input_extension}") 
    

    sound = AudioSegment.from_file(audio_input, format=input_extension)
    print("\n BEFORE REMOVED\n", audio_input)
    if not output:
        output = audio_input
        output = output.replace(input_extension, "wav")

    sound = AudioSegment.from_file(audio_input, input_extension)
    try:
        sound.export(output, format='wav')
        if replace:
            os.remove(audio_input)
            print("\n\nREMOVED\n", audio_input)
    except Exception as x:
        print(x)

    return output

def get_file_extension(path):
    return path.split(".")[-1]

