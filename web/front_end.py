from flask import Blueprint, render_template, request

from bardolph.lib.injection import inject, provide
from web.i_web import WebApp


class FrontEnd:
    def index(self, title='Lights') -> str:
        agent_class = self.get_agent_class()
        js_file = 'lights.js' if agent_class != 'tv' else 'lights_tv.js'
        web_app = provide(WebApp)
        return render_template('index.html',
                               agent_class=agent_class,
                               icon='switch',
                               scripts=web_app.get_buttons(),
                               running=web_app.get_running(),
                               title=title,
                               path_root=web_app.get_path_root(),
                               js_file=js_file)

    @inject(WebApp)
    def run_script(self, path: str, web_app: WebApp) -> str:
        script, running = web_app.get_script(path)
        if running:
            return self.render_action(script, "Running")
        elif script is not None:
            web_app.run_script(script)
            return self.render_action(script, "Started")
        return self.index()

    @inject(WebApp)
    def stop_script(self, path: str, web_app: WebApp):
        script, running = web_app.get_script(path)
        if running:
            web_app.stop_script(path)
        return self.render_action(script, "Stop")

    @inject(WebApp)
    def capture(self, web_app):
        script_control, _ = web_app.get_script('capture')
        if web_app.snapshot():
            msg = ('The current light settings have been captured. Click '
                   '"Retrieve" from the home page to restore those settings.')
        else:
            msg = 'Either the capture failed, or no lights were found.'
        return self.render_action(script_control, msg)

    @inject(WebApp)
    def render_action(self, script, message, web_app):
        agent_class = self.get_agent_class()
        js_file = 'lights.js' if agent_class != 'tv' else 'lights_tv.js'
        if script.button_spec is not None:
            return render_template(
                'button_action.html',
                agent_class=agent_class,
                icon=script.button_spec.icon,
                script=script,
                message=message,
                path_root=web_app.get_path_root(),
                js_file=js_file)
        return render_template(
            'script_action.html',
            agent_class=agent_class,
            title='Bardolph Script',
            file_name=script.file_name,
            icon='litBulb',
            color='#222',
            background_color="Cornsilk",
            message=message,
            path_root=web_app.get_path_root(),
            js_file=js_file)

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


@blueprint.route('/<script_path>')
def run_script(script_path): return fe.run_script(script_path)


@blueprint.route('/stop/<script_path>')
def stop_script(script_path): return fe.stop_script(script_path)


@blueprint.route('/capture')
def capture(): return fe.capture()


@blueprint.route('/status')
def status(): return fe.status()
