from flask import Flask

from bardolph.lib import injection
from web import front_end, web_module


def configure():
    web_module.configure()


def create_app():
    flask_app = Flask(__name__.split('.')[0])
    flask_app.register_blueprint(front_end.blueprint)
    flask_app.add_url_rule("/", endpoint="index")
    return flask_app
