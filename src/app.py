import flask
import api
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base

# Create tables in DB, FastAPI app
Base.metadata.create_all(bind=engine)
app = flask.Flask(__name__)
app.register_blueprint(api.files_routes)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
