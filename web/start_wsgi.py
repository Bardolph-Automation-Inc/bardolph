#!/usr/bin/env python

from waitress import serve

from web import flask_module


def main():
    serve(flask_module.create_app())

if __name__ == "__main__":
    main()
