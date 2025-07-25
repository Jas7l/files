import flask

from api.files import file_bp
from injectors import services
from models.exception import ModuleException
from models.model import BaseOrmMappedModel
from services.database import engine

BaseOrmMappedModel.REGISTRY.metadata.create_all(bind=engine)

app = flask.Flask(__name__)
app.register_blueprint(file_bp)

services.cors_service(app)


@app.errorhandler(ModuleException)
def handle_exception(error: ModuleException):
    response = flask.jsonify(error.json())
    response.status_code = error.code
    return response

