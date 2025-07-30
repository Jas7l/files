import flask

from base_module.models.exception import ModuleException
from base_module.models.logger import setup_logging, LoggerConfig
from injectors.connections import pg
from routers.files import file_bp

app = flask.Flask(__name__)
setup_logging(LoggerConfig(root_log_level='DEBUG'))
pg.setup(app)
app.register_blueprint(file_bp)


@app.errorhandler(ModuleException)
def handle_exception(error: ModuleException):
    response = flask.jsonify(error.json())
    response.status_code = error.code
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
