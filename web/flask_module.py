from flask import Flask

from . import frontend
from bardolph.lib import injection
from . import web_module

"""
Root-level initialization occurs here, as this module is the first one loaded
by Flask to get the app object. That effectively makes this the "main" module.
"""
web_module.configure()
flask_app = Flask(__name__)
flask_app.register_blueprint(frontend.fe)    
flask_app.add_url_rule("/", endpoint="index")
injection.bind_instance(flask_app).to(Flask)


def create_app():
    return injection.provide(Flask)
