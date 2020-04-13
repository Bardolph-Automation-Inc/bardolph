from flask import Flask

from bardolph.lib import injection
from . import front_end
from . import web_module

"""
Root-level initialization occurs here, as this module is the first one loaded
by Flask to get the app object. That effectively makes this the "main" module.
"""
web_module.configure()
_flask_app = Flask(__name__)
_flask_app.register_blueprint(front_end.blueprint)
_flask_app.add_url_rule("/", endpoint="index")
injection.bind_instance(_flask_app).to(Flask)


def create_app():
    return injection.provide(Flask)
