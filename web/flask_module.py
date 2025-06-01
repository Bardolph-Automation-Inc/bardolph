from flask import Flask

from web import front_end, web_module


def configure():
    web_module.configure()


def create_app():
    print('flask_module.create_app()') ###
    configure()
    flask_app = Flask(__name__.split('.')[0])
    flask_app.register_blueprint(front_end.blueprint)
    flask_app.add_url_rule("/", endpoint="index")
    return flask_app
