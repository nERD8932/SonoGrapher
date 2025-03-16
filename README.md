![SonoGrapher Logo](assets/readme_banner.png)

# SonoGrapher

SonoGrapher is an application bundle with a Flask based backend server that uses Ollama and OpenAI's Whisper, along with a PyQt6 frontend for desktop apps. It uses docxtpl and jinja2 to fill a predefined document template with information extracted from the two AI models. It\'s highly customizable and has been built with ease-of-use and robustness in mind.

## Usage

This app has two main parts; the frontend and the backend:

The desktop frontend is a simple PyQt6 interface that uses the `requests` package to make POST requests to the backend, and store the response.

The backend is a Flask based python server. By default, this server uses OpenAI's API for information extraction and audio transcription. If you do not have access to the API, or do not wish to use it, use the `--use-local-llm` & `--use-local-stt` flags while running `app.py` to use Ollama and OpenAI Whisper, and run the models locally. Please keep in mind that both of these frameworks can be computationally intensive. Having a GPU in your server machine is recommended. By default, the server also only runs locally. If you wish to expose the API publicly, you can do so through the Flask environment variables. Keep in mind that you will also have to change the URL the UI connects to, if accessing the API from a different machine.

### Run Backend

Here is a general overview of how to run the backend

- Clone the repository.
- Navigate to the `SonoGrapher` folder.
- Install dependencies through a terminal by using `uv sync`, if you have uv installed (recommended), or by setting up a virtual environment using `pip`.
- (Optional) If you wish to use your GPU for Whisper transcription/Ollama, install [PyTorch with cuda](https://pytorch.org/get-started/locally/).
- Navigate to the `backend` folder.
- Run `build.ps1` on Windows, or `build.sh` on Linux
- A folder called `SonoGrapher Backend v1.x` will have been created in the main directory of the repository. Navigate into it and open the executable to start the server.
- !!NOTE!!: the default rootUser token is `Brhyd7MpfC`; please change this by deleting `backend\api_keys.sqlite` and creating `backend\system_prompt.txt` with a secure key.

### Run Desktop Frontend

Here is a general overview of how to run the desktop frontend

- Clone the repository.
- Navigate to the `SonoGrapher` folder.
- Install dependencies through a terminal by using `uv sync`, if you have uv installed (recommended), or by setting up a virtual environment using `pip`.
- Run `build_frontend.ps1` on Windows, or `build_frontend.sh` on Linux
- A folder called `SonoGrapher Frontend v1.x` will have been created in the main directory of the repository. Navigate into it and open the executable to start the server.

## Contact

Feel free to contact me on [Discord](https://discordapp.com/users/296659492588879885) or on [Linkedin](https://www.linkedin.com/in/samir-amin-sheikh/)

