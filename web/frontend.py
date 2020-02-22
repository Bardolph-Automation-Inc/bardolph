#!/usr/bin/env python
from flask import Blueprint, render_template, request

from bardolph.lib.injection import inject, provide

from .i_web import WebApp

class ScriptFrontEnd:
    def index(self, title='Lights'):
        a_class = ScriptFrontEnd.get_agent_class()
        web_app = provide(WebApp)
        return render_template('index.html',
                               agent_class=a_class,
                               icon='switch',
                               scripts=web_app.get_script_list(),
                               title=title,
                               path_root=web_app.get_path_root())

    @inject(WebApp)
    def run_script(self, script_path, web_app):
        script_info = web_app.get_script(script_path)
        if script_info is not None:
            web_app.queue_script(script_info)
            return self.render_launched(script_info)
        return self.index()

    @inject(WebApp)
    def off(self, web_app):
        script_info = web_app.get_script('off')
        web_app.request_stop()
        web_app.queue_script(script_info)
        return render_template(
            'launched.html',
            agent_class=self.get_agent_class(),
            icon='darkBulb',
            script=script_info,
            path_root=web_app.get_path_root())

    @inject(WebApp)
    def capture(self, web_app):
        web_app.snapshot()
        return self.index()

    @inject(WebApp)
    def stop(self, stop_background, web_app):
        web_app.request_stop(stop_background)
        return self.index('Stopped')

    @inject(WebApp)
    def window_on(self, web_app):
        web_app.queue_file('mz-on.ls')
        web_app.queue_file('mz-red-green.ls', True, True)
        web_app.queue_file('mz-blue-green.ls', True, True)

    @inject(WebApp)
    def render_launched(self, script_info, web_app):
        return render_template(
            'launched.html',
            agent_class=self.get_agent_class(),
            icon=script_info.icon,
            script=script_info,
            path_root=web_app.get_path_root())

    @inject(WebApp)
    def status(self, web_app):
        return render_template(
            "status.html",
            title="Status",
            agent_class=self.get_agent_class(),
            data=web_app.get_status(),
            path_root=web_app.get_path_root())

    @classmethod
    def get_agent_class(cls):
        """ return a string containing 'tv', 'mobile', or 'desktop' """
        header = request.headers.get('User-Agent').lower()
        if header.find('android') != -1 or header.find('iphone') != -1:
            return 'mobile'
        if header.find('smarttv') != -1:
            return 'tv'
        return 'desktop'


fe = Blueprint('scripts', __name__)
sfe = ScriptFrontEnd()

@fe.route('/')
def index(): return sfe.index()

@fe.route('/capture')
def capture(): return sfe.capture()

@fe.route('/off')
def off(): return sfe.off()

@fe.route('/status')
def status(): return sfe.status()

@fe.route('/stop')
def stop(): return sfe.stop(False)

@fe.route('/stop-all')
def stop_all(): return sfe.stop(True)

@fe.route('/window-on')
def window_on(): return sfe.window_on()

@fe.route('/<script_path>')
def run_script(script_path): return sfe.run_script(script_path)
