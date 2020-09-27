#!/usr/bin/env python

from flup.server.fcgi import WSGIServer
from web.flask_module import create_app

if __name__ == '__main__':
    WSGIServer(create_app()).run()
