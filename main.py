from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import models, database
from routers import auth, measurements, reports

# Create DB tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="GlucoTakip", description="Şeker Takip Uygulaması")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Routers
app.include_router(auth.router)
app.include_router(measurements.router)
app.include_router(reports.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
