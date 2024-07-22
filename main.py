from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import credentials, initialize_app

from qasys import config
from qasys.dependencies import get_current_user_id, verify_token
from qasys.routes import pdf, qa, user

app = FastAPI()

# Initialize Firebase app if FIREBASE_DATABASE_URL is set
cred = credentials.Certificate(config.settings.FIREBASE_CREDENTIALS_PATH)
initialize_app(cred, {"databaseURL": config.settings.FIREBASE_DATABASE_URL})

security = HTTPBearer()


app.include_router(pdf.router, prefix="/pdf", tags=["pdf"])
app.include_router(qa.router, prefix="/qa", tags=["qa"])
app.include_router(user.router, prefix="/user", tags=["user"])


@app.middleware("http")
async def authenticate_user(request, call_next):
    if request.url.path.startswith(("/pdf", "/qa", "/user")):
        token = request.headers.get("Authorization")
        if not token:
            raise HTTPException(status_code=401, detail="Missing authentication token")
        user_id = await verify_token(token)
        request.state.user_id = user_id
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
