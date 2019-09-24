#!/usr/bin/env python3

from flup.server.fcgi import WSGIServer
from web.flask_module import create_app

if __name__ == '__main__':
    WSGIServer(create_app()).run()
