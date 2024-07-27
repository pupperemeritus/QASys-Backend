import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi.responses import JSONResponse
from typing import Annotated
from firebase_admin import credentials, initialize_app, auth

from qasys.config import settings
from qasys.dependencies import verify_token
from qasys.routes import pdf, qa, user


def main():
    app = FastAPI()

    cred = credentials.Certificate(
        settings.FIREBASE_CREDENTIALS_FILENAME.get_secret_value()
    )
    initialize_app(cred, options={"projectId": settings.PROJECT_ID})

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def authenticate_user(request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[1]
            try:
                user_id = await verify_token(token)
                request.state.user_id = user_id
            except HTTPException as exc:
                return JSONResponse(
                    status_code=exc.status_code, content={"detail": exc.detail}
                )
        response = await call_next(request)
        return response

    app.include_router(pdf.router, prefix="/pdf", tags=["pdf"])
    app.include_router(qa.router, prefix="/qa", tags=["qa"])
    app.include_router(user.router, prefix="/user", tags=["user"])

    uvicorn.run(app, host="127.0.0.1", port=8000)
