import uuid

import flask
import torch
import torchaudio
import io
from flask import Flask, request, Response, abort, send_file
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
from database import create_connection
import argparse
import json
from docxtpl import DocxTemplate



class Backend:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        # Set up logging obj
        self.log = self.logging_bp()
        # Local or API flag
        self.use_local = True

        # Load API Keys from db
        self.db = create_connection('./backend/api_keys.sqlite', self.log)
        self.api_keys = {x[0]: x[1] for x in self.db.execute('select * from api_keys').fetchall()}

        # Load Speech-To-Text through Whisper
        self.stt = self.load_whisper(local=self.use_local)

        # Load Deepseek-R1 into memory.
        self.system_prompt = '''
You need to extract sonography information from a given text and output it in the following JSON format.
If the information does not exist, fill the section with "UNKNOWN" or "NOT APPLICABLE". Here is the format to follow:
{
  "patientInfo": {
    "name": "<str: Patient Name>",
    "sex": "<str: Gender>",
    "age": "<int: Age>",
    "date": "<str: Current Examination Date>",
    "referringPhysician": "<str: Referring Physician>",
    "uniqueId": "<str: Unique ID>"
  },
  "examinationDetails": {
    "type": "<str: Examination Type>",
    "lastMenstrualPeriod": "<str: LMP Date>",
    "estimatedDeliveryDate": "<str: EDD>",
    "gestationalAge": {
      "weeks": "<int: Weeks>",
      "days": "<int: Days>"
    }
  },
  "findings": "<str: Free-text description of observations (e.g., organ status, fetal measurements, anomalies, fluid presence, etc.)>",
  "measurements": {
    "fetalParameters": [
      {
        "name": "<str: Parameter Name (e.g., BPD, HC, FL)>",
        "value": "<float: Value>",
        "unit": "<str: Unit>"
      }
    ],
    "organMetrics": [
      {
        "organ": "<str:Organ Name (e.g., Uterus, Kidney)>",
        "size": "<str: Dimensions>",
        "thickness": "<str: Thickness>",
        "other": "<str: Additional metrics>"
      }
    ],
    "dopplerIndices": [
      {
        "artery": "<str: Artery Name>",
        "PI": "<str: Pulsatility Index>",
        "RI": "<str: Resistive Index>",
        "SD": "<str: Systolic/Diastolic Ratio>"
      }
    ]
  },
  "comments": list: [
    "<str: Clinical summary or notable observations >"
  ],
  "clinicalCorrelation": list: [
    "<str: Recommendations for follow-up or additional tests>"
    ],
}

Do not deviate from the format.
'''
        ollama.generate(model='deepseek-r1:7b', keep_alive=20.0, system=self.system_prompt)

        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/api/generate-report', methods=["POST"])
        def generate_report() -> Response:
            ak = request.headers.get("Authorization").split(" ")[1]
            self.validate_key(ak)
            extra = {'user': f"[@{self.api_keys[ak]}]", 'bearer_token': f"[Bearer {ak}]"}
            self.log.info(f"Document generation request received.", extra=extra)
            try:
                if 'audio' in request.files:
                    # abort(400, "Missing audio file.")
                    self.log.info(f"Audio file transcription started.", extra=extra)
                    data = self.convert_audio(request.files['audio'], ak)
                    self.log.info(f"Audio file transcription finished.", extra=extra)
                    if type(data) is not str:
                        self.log.error(f"Audio file transcription failed.", extra=extra)
                        return data
                    self.log.info(f"Transcribed text: {data}", extra=extra)
                else:
                    self.log.info(f"Text data assigned.", extra=extra)
                    data = str(request.get_data())
                
                self.log.info(f"Started LLM generation.", extra=extra)
                result = ollama.generate(prompt=f"{self.system_prompt}\nHere is the paragraph:\n {data}", model='deepseek-r1:7b', system=self.system_prompt)
                
                self.log.info(f"LLM finished generating response, creating document...", extra=extra)
                json_obj = json.loads(result['response'].split('```json\n')[1].split('```')[0])
                dt = DocxTemplate("./backend/SonoGrapherTemplate.docx")
                dt.render({"doc": json_obj})
                dt.save(f"./backend/generated/{ak}.docx")
                
                self.log.info(f"Done!", extra=extra)
                return send_file(f"generated\\{ak}.docx", as_attachment=True, download_name='report.docx')
            
            except Exception as e:
                self.log.error(e, extra=extra)
                return Response("An error has occurred, please try again later!", mimetype="text/plain")


    def convert_audio(self, audio, ak) -> Response or str:
        try:
            file = bytearray(audio.read())
            with open(f'./backend/uploaded/{ak}.wav', mode='bx') as f:
                f.write(file)

            if self.use_local:
                result = self.stt.transcribe(f'./backend/uploaded/{ak}.wav')
            else:
                audio_file = open(f'./backend/uploaded/{ak}.wav', mode='rb')
                transcription = self.stt.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
                result = {'text': transcription.text}

            return result["text"]

        except Exception as e:
            self.log.error(e)
            return Response("An error has occurred with transcription, please try again later!", mimetype="text/plain")

        finally:
            if os.path.exists(f"./backend/uploaded/{ak}.wav"):
                os.remove(f'./backend/uploaded/{ak}.wav')

    @staticmethod
    def logging_bp():
        class CustomFormatter(logging.Formatter):
            def format(self, record):
                if record.__dict__.get('user', None) is None:
                    record.__dict__['user'] = ""
                    record.__dict__['bearer_token'] = ""

                s = super().format(record)
                return s

        l = logging.getLogger()
        l.setLevel(logging.INFO)

        if not os.path.exists('./backend/logs/'):
            os.mkdir('./backend/logs/')

        fh = RotatingFileHandler('./backend/logs/debug.log', maxBytes=8096, backupCount=5)
        fh.setLevel(logging.INFO)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = CustomFormatter(
            '[%(levelname)s] @ %(asctime)s - %(user)s %(bearer_token)s %(message)s', "%Y-%m-%d %H:%M:%S")
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        l.addHandler(ch)
        l.addHandler(fh)
        return l

    def validate_key(self, key: str):
        if key not in self.api_keys:
            abort(401, "Invalid API key.")

    def load_whisper(self, local=False):
        if local:
            try:
                if not os.path.exists('./backend/uploaded/'):
                    os.mkdir('./backend/uploaded/')
                device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                self.log.info(f'Using {"GPU" if device.type == "cuda" else "CPU"} device for Speech-to-Text.')
                return whisper.load_model("base", device=device)
            except Exception as e:
                self.log.critical(e)
                exit(-10)
        else:
            client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            return client



backend = Backend()
app = backend.app  # Expose Flask app instance
