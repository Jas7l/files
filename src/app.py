import flask

from routers.files import file_bp
from injectors.connections import pg
from base_module.models.exception import ModuleException

app = flask.Flask(__name__)
pg.setup(app)
app.register_blueprint(file_bp)


@app.errorhandler(ModuleException)
def handle_exception(error: ModuleException):
    response = flask.jsonify(error.json())
    response.status_code = error.code
    return response
