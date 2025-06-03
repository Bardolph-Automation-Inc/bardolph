#!/usr/bin/env python
from flask import Blueprint, render_template, request

from bardolph.lib.injection import inject, provide
from web.i_web import WebApp


class FrontEnd:
    def index(self, title='Lights'):
        a_class = FrontEnd.get_agent_class()
        web_app = provide(WebApp)
        return render_template('index.html',
                               agent_class=a_class,
                               icon='switch',
                               scripts=web_app.get_script_list(),
                               title=title,
                               path_root=web_app.get_path_root())

    @inject(WebApp)
    def run_script(self, path, web_app):
        script_control = web_app.get_script_control(path)
        if script_control is not None:
            if script_control.running or web_app.queue_script(script_control):
                return self.render_action(script_control, "Started")
        return self.index()

    @inject(WebApp)
    def off(self, web_app):
        script_control = web_app.get_script_control('off')
        web_app.stop_current()
        web_app.queue_script(script_control)
        return self.render_action(script_control, "")

    @inject(WebApp)
    def capture(self, web_app):
        script_control = web_app.get_script_control('capture')
        script_control.title = ''
        if web_app.snapshot():
            msg = ('The current light settings have been captured. Click '
                   '"Retrieve" from the home page to restore those settings.')
        else:
            msg = 'Either the capture failed, or no lights were found.'
        return self.render_action(script_control, msg)

    @inject(WebApp)
    def stop_script(self, path, web_app):
        script_control = web_app.get_script_control(path)
        if script_control is not None and script_control.running:
            web_app.stop_script(path)
            return self.render_action(script_control, "Stop Requested")
        return self.index()

    @inject(WebApp)
    def stop_current(self, web_app):
        script_control = web_app.get_script_control('stop-current')
        web_app.stop_current()
        return self.render_action(script_control, "Requested")

    @inject(WebApp)
    def stop_all(self, web_app):
        script_control = web_app.get_script_control('stop-all')
        web_app.stop_all()
        return self.render_action(script_control, "Requested")

    @inject(WebApp)
    def render_action(self, script_control, message, web_app):
        return render_template(
            'action.html',
            agent_class=self.get_agent_class(),
            icon=script_control.icon,
            script=script_control,
            message=message,
            path_root=web_app.get_path_root())

    @inject(WebApp)
    def status(self, web_app):
        return render_template(
            "status.html",
            title="Status",
            agent_class=self.get_agent_class(),
            data=web_app.get_status(),
            path_root=web_app.get_path_root())

    @staticmethod
    def get_agent_class():
        """ return a string containing 'tv', 'mobile', or 'desktop' """
        header = request.headers.get('User-Agent').lower()
        if header.find('android') != -1 or header.find('iphone') != -1:
            return 'mobile'
        if header.find('smarttv') != -1:
            return 'tv'
        return 'desktop'


blueprint = Blueprint('scripts', __name__)
fe = FrontEnd()

@blueprint.route('/')
def index(): return fe.index()

@blueprint.route('/capture')
def capture(): return fe.capture()

@blueprint.route('/off')
def off(): return fe.off()

@blueprint.route('/status')
def status(): return fe.status()

@blueprint.route('/stop/<script_path>')
def stop_script(script_path): return fe.stop_script(script_path)

@blueprint.route('/stop-current')
def stop_current(): return fe.stop_current()

@blueprint.route('/stop-all')
def stop_all(): return fe.stop_all()

@blueprint.route('/<script_path>')
def run_script(script_path): return fe.run_script(script_path)
