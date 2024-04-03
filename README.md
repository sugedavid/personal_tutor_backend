# Personal Tutor Backend

Backend for the Personal Tutor Client

## Get Started

1. Create a virtual environment to install the libraries. For example, using venv.

2. To activate an existing environment:

   - On Windows: `.venv\Scripts\activate`

   - On MacOS: `source .venv/bin/activate`

3. Install libraries defined in the requirements.txt file:

   ```
   pip3 install -r requirements.txt
   ```

4. To run the server, create a new run configuration for FastAPI:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python Debugger: FastAPI",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload"],
      "jinja": true
    }
  ]
}
```

5. Create a .env file at the root of the project and add the following key:
   ```
   PERSONAL_TUTOR_OPENAI_API_KEY
   ```
6. Add a `serviceAccountKey.json` file at the root of the project. This contains credentials used to authenticate and authorize access to Firebase services.

## Docker

1. Launch the Docker application.

2. To build the Docker image, use the command at the root of the project:

```
docker build -t personal_tutor_backend .
```

3. To run the Docker container, use the command at the root of the project:

```
docker run --env-file .env -d -p 8000:8000 personal_tutor_backend
```
