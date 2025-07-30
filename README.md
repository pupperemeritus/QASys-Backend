# Q&A System - FastAPI Backend

This is the backend for a Question & Answering application, built with FastAPI. It handles user authentication, PDF processing, and answering questions based on the uploaded documents.

## Features

- **PDF Upload:** Endpoint to receive and process PDF files.
- **Q&A Endpoint:** Receives questions and returns answers.
- **User Authentication:** Secures endpoints using Firebase Authentication. All requests to protected routes require a `Bearer` token.
- **CORS Enabled:** Allows requests from any origin.

## API Endpoints

- `POST /pdf/upload`: Upload a PDF file. Requires authentication.
- `POST /qa/ask`: Ask a question. Requires authentication.
- `POST /user/...`: User-related endpoints (e.g., registration, login).

## Getting Started

### Prerequisites

- Python 3.8+
- A Firebase project and service account credentials file.

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/pupperemeritus/QASys-Backend.git
    cd QASys-Backend
    ```

2. **Install dependencies:**

    ```bash
    pip install fastapi uvicorn "firebase-admin[auth]" python-multipart
    ```

    _(It's recommended to create a `requirements.txt` file for your project)_

3. **Environment Variables:**
    - Ensure your Firebase service account JSON file is available and its path is correctly configured in your settings (e.g., via an environment variable `FIREBASE_CREDENTIALS_FILENAME`).
    - Set your Firebase Project ID in your settings (`PROJECT_ID`).

### Running the Application

```bash
uvicorn main:main --host 127.0.0.1 --port 8000 --reload
```
