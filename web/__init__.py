import sys
sys.path.append('..')

from flask import Flask
from web import frontend

def create_app():
    flask_app = Flask(__name__)
    flask_app.register_blueprint(frontend.fe)    
    flask_app.add_url_rule("/", endpoint="index")
    return flask_app
