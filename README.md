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

5. Create a .env file and add the following keys:
   ```
   FIREBASE_API_KEY
   PERSONAL_TUTOR_OPENAI_API_KEY
   ```
