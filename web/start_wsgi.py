#!/usr/bin/env python

from waitress import serve

from web import flask_module


def main():
    print('start_wsgi.main()') ###
    ### flask_module.configure()
    serve(flask_module.create_app())

if __name__ == "__main__":
    main()
