import torch
from flask import Flask, request, Response, abort, send_file, send_from_directory
import ollama
import whisper
from openai import OpenAI
from pprint import pprint
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import os
from database import create_connection, create_default, create_table
import argparse
import json
from docxtpl import DocxTemplate
import sys
from Markdown2docx import Markdown2docx



class Backend:
    def __init__(self,
                 use_local_stt=False,
                 use_local_llm=False,
                 local_llm="gemma3",
                 local_stt="base",
                 openai_llm="gpt-4o-mini",
                 openai_stt="whisper-1",
                 openai_key=os.environ.get("OPENAI_API_KEY", ""),
                 markdown=False):

        # Set up logging obj
        self.log = self.logging_bp()
        # Local or API flag
        self.use_local_stt = use_local_stt
        self.use_local_llm = use_local_llm
        self.openai_llm = openai_llm
        self.openai_stt = openai_stt
        self.local_llm = local_llm
        self.local_stt = local_stt
        self.openai_key = openai_key
        self.markdown = markdown

        if not self.use_local_llm or not self.use_local_stt:
            if self.openai_key == "":
                self.log.critical("You forgot to set your OpenAI API key. Please set it and reopen the app.")
                input("Press any key to exit...")
                sys.exit(-9)

        # Load API Keys from db
        if not os.path.exists("./backend/api_keys.sqlite"):
            create_table()
            create_default()

        self.db = create_connection('./backend/api_keys.sqlite', self.log)
        cursor = self.db.cursor()

        self.api_keys = {x[0]: x[1] for x in cursor.execute('select * from main.api_keys').fetchall()}

        self.db.close()

        # Load Speech-To-Text through Whisper
        self.stt = self.load_whisper()

        # Load Deepseek-R1 into memory.
        self.system_prompt = ""
        if self.markdown:
            with open('./backend/system_prompt_markdown.txt', 'r') as f:
                self.system_prompt = f.read()
        else:
            with open('./backend/system_prompt.txt', 'r') as f:
                self.system_prompt = f.read()

        if self.use_local_llm:
            try:
                os.system(f"ollama pull {self.local_llm}")
                ollama.generate(model=self.local_llm, keep_alive=20.0, system=self.system_prompt)
            except Exception as e:
                self.log.critical(e)
                input("Press any key to exit...")
                sys.exit(-11)

        staticDir = os.getcwd() + '/webpage'
        self.app = Flask(__name__, static_folder=staticDir)
        self.setup_routes()
        # pprint(vars(self))

    def setup_routes(self):
        @self.app.route('/', defaults={'path': ''})
        @self.app.route('/<path:path>')
        def serve(path):
            if path != "" and os.path.exists(self.app.static_folder + '/' + path):
                return send_from_directory(self.app.static_folder, path)
            else:
                return send_from_directory(self.app.static_folder, 'index.html')

        @self.app.route('/api/generate-report', methods=["POST"])
        def generate_report() -> Response:
            ak = request.headers.get("Authorization").split(" ")[1]
            self.validate_key(ak)
            extra = {'user': f"[@{self.api_keys[ak]}]", 'bearer_token': f"[Bearer {ak}]"}
            self.log.info(f"Document generation request received.", extra=extra)
            try:
                if 'audio' in request.files:
                    self.log.info(f"Using audio file.", extra=extra)
                    self.log.info(f"Audio file transcription started.", extra=extra)
                    data = self.convert_audio(request.files['audio'], ak, extra)
                    self.log.info(f"Audio file transcription finished.", extra=extra)
                    if type(data) is not str:
                        self.log.error(f"Audio file transcription failed.", extra=extra)
                        return data
                    self.log.info(f"Transcribed text: {data}", extra=extra)
                elif 'text' in request.files:
                    self.log.info(f"Using text file.", extra=extra)
                    data = self.extractText(request.files['text'], ak, extra)
                else:
                    self.log.info(f"User request had no file attached!", extra=extra)
                    abort(400, "No file attached!")

                self.log.info(f"Started LLM generation.", extra=extra)

                prompt = f"{self.system_prompt}\nHere is the paragraph:\n {data}"
                if self.use_local_llm:
                    result = ollama.generate(prompt=prompt, model=self.local_llm, system=self.system_prompt)
                else:
                    client = OpenAI(api_key=self.openai_key)
                    response = client.responses.create(
                        model=self.openai_llm,
                        instructions=self.system_prompt,
                        input=prompt)
                    result = {'response': response.output_text}

                self.log.info(f"LLM finished generating response, creating document...", extra=extra)

                if self.markdown:
                    with open(f"./backend/generated/{ak}.md", 'w') as f:
                        f.write(result['response'])
                    project = Markdown2docx(f"./backend/generated/{ak}")
                    project.eat_soup()
                    project.save()
                else:
                    json_obj = json.loads(result['response'].split('```json\n')[1].split('```')[0])
                    self.log.info(json_obj, extra=extra)
                    dt = DocxTemplate("./backend/SonoGrapherTemplate.docx")
                    dt.render({"doc": json_obj})
                    dt.save(f"./backend/generated/{ak}.docx")
                
                self.log.info(f"Done!", extra=extra)
                p = os.path.join(os.getcwd(), "backend\\generated", f"{ak}.docx")
                # self.log.info(p, extra=extra)
                response = send_file(p, as_attachment=True, download_name='report.docx')
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
            
            except Exception as e:
                self.log.error(e, extra=extra)
                response = Response("An error has occurred, please try again later!", mimetype="text/plain", )
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response


    def convert_audio(self, audio, ak, extra) -> Response or str:
        try:
            file = bytearray(audio.read())
            with open(f'./backend/uploaded/{ak}.wav', mode='bx') as f:
                f.write(file)

            if self.use_local_stt:
                result = self.stt.transcribe(f'./backend/uploaded/{ak}.wav')
            else:
                audio_file = open(f'./backend/uploaded/{ak}.wav', mode='rb')
                transcription = self.stt.audio.transcriptions.create(
                    model=self.openai_stt,
                    file=audio_file,
                    response_format="text"
                )
                result = {'text': transcription.text}

            return result["text"]

        except Exception as e:
            self.log.error(e, extra=extra)
            response = Response("An error has occurred with transcription, please try again later!", mimetype="text/plain")
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        finally:
            if os.path.exists(f"./backend/uploaded/{ak}.wav"):
                os.remove(f'./backend/uploaded/{ak}.wav')

    def extractText(self, text, ak, extra):
        try:
            file = bytearray(text.read())
            with open(f'./backend/uploaded/{ak}.txt', mode='bx') as f:
                f.write(file)
            text = ""
            with open(f'./backend/uploaded/{ak}.txt', mode='r') as f:
                text = f.read()
            return text
        except Exception as e:
            self.log.error(e, extra=extra)
            response =  Response("An error occurred while reading the file, please try again later!", mimetype="text/plain")
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        finally:
            if os.path.exists(f"./backend/uploaded/{ak}.txt"):
                os.remove(f'./backend/uploaded/{ak}.txt')

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
            self.log.info(f"Invalid API key used: {key}")
            abort(401, "Invalid API key.")

    def load_whisper(self):
        if self.use_local_stt:
            try:
                if not os.path.exists('./backend/uploaded/'):
                    os.mkdir('./backend/uploaded/')
                device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                self.log.info(f'Using {"GPU" if device.type == "cuda" else "CPU"} device for Speech-to-Text.')
                return whisper.load_model(self.local_stt, device=device)
            except Exception as e:
                self.log.critical(e)
                input("Press any key to exit...")
                sys.exit(-10)
        else:
            client = OpenAI(api_key=self.openai_key)
            return client

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog='SonoGrapher Backend',
        description='SonoGrapher Backend works by hosting a simple Flask-based server that '
                    '(with the help of Ollama and OpenAI\'s Whisper) lets you convert text/audio '
                    'sonography session data into a cohesive docx report in just a few clicks. It\'s highly '
                    'customizable and has been built with ease-of-use and robustness in mind.',
        epilog='Feel free to contact the developer (me) @nerd8932 on Discord or GitHub\n')

    parser.add_argument('--use-local-llm',
                        help='Use Ollama to run an LLM locally for prompting.',
                        action='store_true',
                        dest='use_local_llm')

    parser.add_argument('--use-local-stt',
                        help='Use Whisper to convert Speech-to-Text locally.',
                        action='store_true',
                        dest="use_local_stt")

    local_stt_choices=['tiny', 'base', 'small', 'medium', 'large', 'turbo', 'tiny.en', 'base.en', 'small.en', 'medium.en']
    parser.add_argument('--local-stt-model',
                        type=str,
                        default="base",
                        help='Which Whisper model to use.',
                        choices=local_stt_choices,
                        dest="local_stt_model")

    parser.add_argument('--local-llm-model',
                        type=str,
                        default="gemma3",
                        help='Which Ollama model to use. Look at the possible options at https://ollama.com/search',
                        dest="local_llm_model")

    parser.add_argument('--openai-llm-model',
                        type=str,
                        default="gpt-4o-mini",
                        help='Which OpenAI model to use for prompting. '
                             'Look at the possible options at https://platform.openai.com/docs/models. '
                             'Please be sure to use the --openai-api-key flag to set your API key, if you haven\'t set it '
                             'already in your .env file or your environment variables.',
                        dest="openai_llm_model")

    parser.add_argument('--openai-stt-model',
                        type=str,
                        default="whisper-1",
                        help='Which OpenAI model to use for Speech-to-Text. '
                             'Look at the possible options at https://platform.openai.com/docs/models. '
                             'Please be sure to use the --openai-api-key flag to set your API key, if you haven\'t set it '
                             'already in your .env file or your environment variables.',
                        dest="openai_stt_model")

    parser.add_argument('--openai-api-key',
                        type=str,
                        default=os.environ.get("OPENAI_API_KEY", ""),
                        help='API key for OpenAI models incase you\'re not running models locally.',
                        dest="openai_api_key")

    parser.add_argument('--host',
                        type=str,
                        default='0.0.0.0',
                        help='Host IP address.',
                        dest="host")

    parser.add_argument('--port',
                        type=str,
                        default='5000',
                        help='Host port.',
                        dest="port")

    parser.add_argument('--debug',
                        action='store_true',
                        help='Set Flask Debug flag',
                        dest="debug")

    parser.add_argument('--generate-markdown',
                        action='store_true',
                        help='Generate a report through MarkDown instead of JSON',
                        dest="markdown")

    args = parser.parse_args()
    print(
        r'''

     ____                     ____                 _
    / ___|  ___  _ __   ___  / ___|_ __ __ _ _ __ | |__   ___ _ __
    \___ \ / _ \| '_ \ / _ \| |  _| '__/ _` | '_ \| '_ \ / _ \ '__|
     ___) | (_) | | | | (_) | |_| | | | (_| | |_) | | | |  __/ |
    |____/ \___/|_| |_|\___/ \____|_|  \__,_| .__/|_| |_|\___|_|
                                            |_|

    ''')
    parser.print_help()
    backend = Backend(use_local_llm=args.use_local_llm,
                      use_local_stt=args.use_local_stt,
                      openai_llm=args.openai_llm_model,
                      openai_stt=args.openai_stt_model,
                      local_llm=args.local_llm_model,
                      local_stt=args.local_stt_model,
                      openai_key=args.openai_api_key,
                      markdown=args.markdown)

    backend.app.run(debug=args.debug, host=args.host, port=args.port)
