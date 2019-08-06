#!/usr/bin/env python
from flask import Blueprint, Flask, render_template, request

from bardolph.lib.injection import provide

from . import web_module
from .web_app import WebApp
    
web_module.configure()

class ScriptFrontEnd:
    def __init__(self):
        self.web_app = provide(WebApp)
        
    def index(self, title='Lights'):
        ac = self.get_agent_class()
        return render_template('index.html',
            agent_class=ac,
            icon = 'switch',
            scripts=self.web_app.get_script_list(),
            title=title,
            path_root=self.web_app.get_path_root())  
    
    def run_script(self, script_path):
        script_info = self.web_app.get_script(script_path)
        if script_info is not None:
            self.web_app.queue_script(script_info)
            return self.render_launched(script_info)
        else:
            return self.index()

    def off(self):
        script_info = self.web_app.get_script('off')
        self.web_app.request_stop()
        self.web_app.queue_script(script_info)
        return render_template(
            'launched.html',
            agent_class=self.get_agent_class(),
            icon='darkBulb',
            script=script_info,
            path_root=self.web_app.get_path_root())
  
    def capture(self):
        self.web_app.snapshot()
        return self.index()

    def stop(self):
        self.web_app.request_stop()
        return self.index('Stopped')
    
    def render_launched(self, script_info):
        return render_template(
            'launched.html',
            agent_class=self.get_agent_class(),
            icon=script_info.icon,
            script=script_info,
            path_root=self.web_app.get_path_root())
        
    def status(self):
        return render_template(
            "status.html",
            title="Status",
            agent_class=self.get_agent_class(),
            data=self.web_app.get_status(),
            path_root=self.web_app.get_path_root())
        
    def get_agent_class(self):
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
def stop(): return sfe.stop()

@fe.route('/<script_path>')
def run_script(script_path): return sfe.run_script(script_path)
