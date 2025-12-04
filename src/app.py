import flask
import redis
from base_module.models.exception import ModuleException
from base_module.models.logger import setup_logging, LoggerConfig
from flask_cors import CORS
from injectors.connections import pg
from routers.auth import auth_bp
from routers.files import file_bp

app = flask.Flask(__name__)

app.config['JWT_SECRET'] = 'supersecret'
app.config['JWT_ALGO'] = 'HS256'
app.config['JWT_TTL_SECONDS'] = 24 * 3600

setup_logging(LoggerConfig(root_log_level='DEBUG'))

app.redis = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
pg.setup(app)

app.register_blueprint(file_bp)
app.register_blueprint(auth_bp)
CORS(app, resources={r'/api/*': {'origins': '*'}})


@app.errorhandler(ModuleException)
def handle_exception(error: ModuleException):
    response = flask.jsonify(error.json())
    response.status_code = error.code
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
