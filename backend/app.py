from flask import Flask
import ollama
import dotenv

app = Flask("sonographer_backend")


@app.route('/api/convert-audio', methods=["POST"])
def convert_audio():
    pass


@app.route('/api/generate-report', methods=["POST"])
def generate_report():
    pass


if __name__ == '__main__':
    app.run()
