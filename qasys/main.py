from fastapi import Depends, FastAPI
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import credentials, initialize_app

from qasys.config import settings
from qasys.dependencies import verify_token, get_current_user_id
from qasys.routes import pdf, qa


app = FastAPI()

# Initialize Firebase app if FIREBASE_DATABASE_URL is set
if settings.FIREBASE_DATABASE_URL:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    initialize_app(cred, {"databaseURL": settings.FIREBASE_DATABASE_URL})

security = HTTPBearer()

app.include_router(pdf.router, prefix="/pdf", tags=["pdf"])
app.include_router(qa.router, prefix="/qa", tags=["qa"])


@app.post("/clear_user_data")
async def clear_user_data(user_id: str = Depends(get_current_user_id)):
    from qasys.utils import clear_user_data

    clear_user_data(user_id)
    return {"message": "User data cleared successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
