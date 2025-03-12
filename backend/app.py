import flask
import torch
import torchaudio
import io
from flask import Flask, request, Response, abort
import ollama
import whisper
from openai import OpenAI
import soundfile as sf
import pydub
import scipy
import numpy as np
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import os

from numba.cpython.randomimpl import double

from database import create_connection

USE_LOCAL = True

def logging_bp():
    l = logging.getLogger()
    l.setLevel(logging.INFO)

    # File logger
    if not os.path.exists('./backend/logs/'):
        os.mkdir('./backend/logs/')

    fh = RotatingFileHandler('./backend/logs/debug.log', maxBytes=8096, backupCount=5)
    fh.setLevel(logging.INFO)

    # Console logger
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Log format
    formatter = logging.Formatter(
        '[%(levelname)s] @ %(asctime)s - \"%(message)s\"')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    l.addHandler(ch)
    l.addHandler(fh)
    return l

def validate_key(key: str):
    if key not in list(api_keys.keys()):
        abort(401, "Invalid API key.")

def load_whisper(local=False):
    if local:
        try:
            if not os.path.exists('./backend/uploaded/'):
                os.mkdir('./backend/uploaded/')
            device = torch.device('cpu')
            if torch.cuda.is_available():
                device = torch.device('cuda')
                log.info('Using GPU device.')
            return whisper.load_model("medium", device=device)
        except Exception as e:
            log.critical(e)
            exit(-10)
    else:
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        return client

# Logging boiler-plate code
log = logging_bp()

# Load API Keys
db = create_connection('./backend/api_keys.sqlite', log)
api_keys = {x[0]: x[1] for x in db.execute('select * from api_keys').fetchall()}

load_dotenv()
# Load Whisper for Speech-to-Text
stt = load_whisper(local=USE_LOCAL)
# And Deepseek for Information Extraction
# ollama.generate(model='deepseek-r1:7b', keep_alive=20.0)

app = Flask("sonographer_backend")

@app.route('/api/convert-audio', methods=["POST"])
def convert_audio() -> Response:

    # Validate request
    ak = request.headers.get("Authorization").split(" ")[1]
    validate_key(ak)
    log.info(f"Request received from @{api_keys[ak]} with bearer token `{ak}`")

    # Process audio
    if 'audio' not in request.files:
        abort(400, "Missing audio file.")
    try:
        file = bytearray(request.files['audio'].read())
        with open('./backend/uploaded/temp.wav', mode='bx') as f:
            f.write(file)
        if USE_LOCAL:
            # Run Whisper transcription
            result = stt.transcribe('./backend/uploaded/temp.wav')

        else:
            audio_file = open('./backend/uploaded/temp.wav', mode='rb')
            transcription = stt.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            result = {'text': transcription.text}

        print(result)
        return Response(result["text"], mimetype="text/plain")

    except Exception as e:
        log.error(e)
        return Response("An error has occurred, please try again later!", mimetype="text/plain")

    finally:
        if os.path.exists("./backend/uploaded/temp.wav"):
            os.remove('./backend/uploaded/temp.wav')

@app.route('/api/generate-report', methods=["POST"])
def generate_report() -> Response:

    # Validate request
    ak = request.headers.get("Authorization").split(" ")[1]
    validate_key(ak)
    log.info(f"Request received from @{api_keys[ak]} with bearer token `{ak}`")


    # Generate Report
    try:
        result = "Generating report..."
        return Response(result, mimetype="text/plain")
    except Exception as e:
        log.error(e)
        return Response("An error has occurred, please try again later!", mimetype="text/plain")

if __name__ == '__main__':

    # Start app
    app.run()
