from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base
from app.api import files

# Create tables in DB, FastAPI app
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Add router
app.include_router(files.router)
