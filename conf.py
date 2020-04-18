import os
import sys
sys.path.insert(0, 'bardolph/controller')
sys.path.insert(0, 'bardolph/fakes')
sys.path.insert(0, 'bardolph/lib')
sys.path.insert(0, 'bardolph/parser')


project = 'Bardolph'
copyright = '2020, Al Fontes'
author = 'Al Fontes'


extensions = [
]

templates_path = ['_templates']

exclude_patterns = []

html_favicon = 'www/logo_ico.png'
html_theme = 'nature'
html_static_path = ['web/static']
