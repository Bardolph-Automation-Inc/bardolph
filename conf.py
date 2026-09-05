"""
Configuration for sphinx
"""
import os
import sys

print(os.getcwd())

sys.path.insert(0, 'bardolph/controller')
sys.path.insert(0, 'bardolph/fakes')
sys.path.insert(0, 'bardolph/lib')
sys.path.insert(0, 'bardolph/parser')
sys.path.append('.')
from bardolph.pygments import bardolph_lexer

project = 'Bardolph'
copyright = ('2026, Bardolph Automation, Inc. ' +
             'All trademarks mentioned on this website are the property ' +
             'of their respective owners')
author = 'Bardolph Engineering'

from sphinx.highlighting import lexers

lexers ['lightbulb'] = bardolph_lexer.BardolphLexer()
extensions = [
    "sphinx_design",
    "sphinx_copybutton"
]

templates_path = ['_templates']

exclude_patterns = []

root_doc = 'contents'
html_favicon = 'www/logo_ico.png'
html_static_path = ['web/static']
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'analytics_id': 'G-7VQPMY58X8'
}

def setup(app):
    app.add_css_file('styles.css')