#!/usr/bin/env python

from waitress import serve
from web.flask_module import create_app

if __name__ == '__main__':
    serve(create_app(), listen='127.0.0.1')

