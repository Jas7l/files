import flask
from injectors import services
from api.files import file_bp
from models.exception import ModuleException
from services.database import engine
from models.model import BaseOrmMappedModel

# Create tables in DB, FastAPI app
BaseOrmMappedModel.REGISTRY.metadata.create_all(bind=engine)

app = flask.Flask(__name__)
app.register_blueprint(file_bp)

services.cors_service(app)


@app.errorhandler(ModuleException)
def handle_exception(error: ModuleException):
    response = flask.jsonify(error.json())
    response.status_code = error.code
    return response

