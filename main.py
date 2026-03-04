from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

# load_dotenv() MUST be called before importing routers
# because routers/auth.py uses os.getenv at import time!
load_dotenv()

import models, database
from routers import auth, measurements, reports, admin

# Create DB tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="GlucoTakip", description="Şeker Takip Uygulaması")

# SessionMiddleware is required for Authlib OAuth
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "super-secret-default-key"))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Routers
app.include_router(auth.router)
app.include_router(measurements.router)
app.include_router(reports.router)
app.include_router(admin.router)

# .well-known klasörünü dışarı açıyoruz
os.makedirs(".well-known", exist_ok=True)
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)