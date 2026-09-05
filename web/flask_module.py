
from pathlib import Path

from flask import Flask

from web import front_end, web_module


def configure():
    web_module.configure()


def create_app():
    configure()
    current_dir = Path(__file__).resolve().parent
    static_folder = str((current_dir / 'static').resolve())
    template_folder = str((current_dir / 'templates').resolve())

    flask_app = Flask(__name__.split('.')[0],
                      static_folder=static_folder,
                      template_folder=template_folder)
    flask_app.register_blueprint(front_end.blueprint)
    flask_app.add_url_rule("/", endpoint="index")
    return flask_app
