from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

# load_dotenv() MUST be called before importing routers
# because routers/auth.py uses os.getenv at import time!
load_dotenv()

import models, database, crud
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

@app.get("/set-language", tags=["Settings"])
def set_language(lang: str, request: Request, db: Session = Depends(database.get_db)):
    """Dili değiştirir ve referer veya ana sayfaya yönlendirir."""
    referer = request.headers.get("referer", "/")
    # Referer url'i ayni site degilse guvenlik icon anasayfaya atilabilir ama simdilik referer
    response = RedirectResponse(url=referer, status_code=302)
    
    if lang in ["tr", "en"]:
        response.set_cookie(key="language", value=lang, httponly=True, samesite="lax")
        # Update user's DB language if logged in
        user = auth.get_current_user_from_cookie(request, db)
        if user:
            crud.update_user_language(db, user.id, lang)
            
    return response

# .well-known klasörünü dışarı açıyoruz
os.makedirs(".well-known", exist_ok=True)
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)