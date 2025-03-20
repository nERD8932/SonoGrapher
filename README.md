![SonoGrapher Logo](./assets/readme_banner.png)

# **SonoGrapher**

SonoGrapher lets you convert text/audio sonography session data into a cohesive docx report in just a few clicks.

SonoGrapher is an application bundle with a Flask based backend server that uses Ollama and OpenAI's Whisper, along with a PyQt6 frontend for desktop apps. It uses docxtpl and jinja2 to fill a predefined document template with information extracted from the two AI models. It\'s highly customizable and has been built with ease-of-use and robustness in mind.

## Features

* **Dynamic Report Generation:** Converts audio/text inputs into DOCX reports.
* **Flexible AI Integration:** Choose between local models or API-based solutions.
* **Command-Line Configurability:** Fine-tune settings via various command-line flags.
* **Robust Logging:** Built-in logging with rotating file handlers.
* **Customizable Templates:** Edit the system prompt and DOCX template to suit your needs.

## Usage

This app has two main parts; the frontend and the backend:

The desktop frontend is a simple PyQt6 interface that uses the `requests` package to make POST requests to the backend, and store the response.

The backend is a Flask based python server. By default, this server uses OpenAI's API for information extraction and audio transcription. If you do not have access to the API, or do not wish to use it, use the `--use-local-llm` & `--use-local-stt` flags while running `app.py` to use Ollama and OpenAI Whisper, and run the models locally. Please keep in mind that both of these frameworks can be computationally intensive. Having a GPU in your server machine is recommended. By default, the server also only runs locally. If you wish to expose the API publicly, you can do so through the Flask environment variables. Keep in mind that you will also have to change the URL the UI connects to, if accessing the API from a different machine.

### Running the Backend Flask Server

Here is a general overview of how to run the server:

- Clone the repository and navigate to the `SonoGrapher` folder.

  ```bash
  git clone https://github.com/your-repo/SonoGrapher.git
  cd SonoGrapher
  ```
- Install dependencies through a terminal by using `uv sync`, if you have uv installed (recommended), or by setting up a virtual environment using `pip`.

  ```bash
  uv sync
  ```

  OR

  ```bash
  python -m venv .venv
  pip install -r 'requirements_backend.txt'
  ```
- (Optional) If you wish to use your GPU for Whisper transcription/Ollama, install [PyTorch with cuda](https://pytorch.org/get-started/locally/).

  ```bash
  pip install -r 'requirements_cuda.txt'
  ```
- Navigate to the `backend` folder.
- Run `build.ps1` on Windows (right-click and select 'Run with PowerShell'), or `build.sh` on Linux
- A folder called `SonoGrapher_Backend` will have been created in the main directory of the repository. Navigate into it and open the executable to start the server.
- !!NOTE!!: the default rootUser token is `Brhyd7MpfC`; please change this by deleting `backend\api_keys.sqlite` and creating `backend\system_prompt.txt` with a secure key.

Additional features:

- **System Prompt:** Customize the LLM's system prompt and JSON output format in `backend/system_prompt.txt`
- **Template:** Modify the output document template in SonoGrapherTemplate.docx
- **Logging:** Logs are stored in backend/logs/debug.log using a rotating file handler. Temporary uploads are managed in backend/uploaded/.

### Running the React Webapp Frontend

No additional setup necessary! If you've installed the backend, you should be able to access the webapp on the root page (`http://localhost:5000/` by default)

* Drag and drop your file into the designated area, or select it through the file selector.
* Adjust the URI and Auth token if need be, and press generate
* The generated document will automatically get downloaded!

### Running the Desktop Frontend

Here is a general overview of how to run the desktop frontend

- Clone the repository.

  ```bash
  git clone https://github.com/your-repo/SonoGrapher.git
  cd SonoGrapher
  ```
- Navigate to the `SonoGrapher` folder and install dependencies through a terminal by using `uv sync`, if you have uv installed (recommended), or by setting up a virtual environment using `pip`.

  ```bash
  uv sync
  ```

  OR

  ```bash
  python -m venv .venv
  pip install -r 'requirements_frontend.txt'
  ```
- Run `build_frontend.ps1` on Windows (right-click and select 'Run with PowerShell'), or `build_frontend.sh` on Linux
- An executable called `SonoGrapher_Frontend(.exe)` will have been created in the main directory of the repository. Navigate into it and open the executable to start the server.
- !!NOTE!!: Please remember to define `BEARER_TOKEN` and `API_URL` in your environment variables, or a .env file, if they differ from the default. You should not use the default token in a production environment

## API Endpoint

* **Generate Report:**`POST /api/generate-report`
  * Accepts audio or text files.
  * Requires an API key in the header.
  * Processes the file with AI (local or API-based) and returns a DOCX report.
  * Request format - Include bearer token in header, attach form-data file with key 'text' for a `.txt` file or 'audio' for a `.wav` file

## Contact

Feel free to contact me on [Discord](https://discordapp.com/users/296659492588879885) or on [Linkedin](https://www.linkedin.com/in/samir-amin-sheikh/)

## License

This project is licensed under the terms of the GNU General Public License v3.0. See the [LICENSE](./LICENSE) file for details.
