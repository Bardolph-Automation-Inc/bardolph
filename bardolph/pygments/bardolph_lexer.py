from pygments.lexer import RegexLexer, words
from pygments.token import Text, Keyword, Comment, Number, Operator, String
from pygments.token import Whitespace

class BardolphLexer(RegexLexer):
    name = 'LS'
    aliases = ['ls', 'lightbulb']
    filenames = ['*.ls']

    tokens = {
        'root': [
            (r'#.*?$', Comment),
            (r'-?[0-9]*?\.[0-9]+$', Number.Float),
            (r'-?[0-9]+$', Number.Integer),
            (r'[+*/<>=%-\{\}]', Operator),
            (words((
                'all', 'and', 'assign', 'at', 'begin', 'brightness',
                'cycle', 'define',
                'else', 'end', 'from', 'get', 'group', 'groups', 'hue',
                'if', 'kelvin', 'lights',
                'location', 'locations', 'on', 'or', 'power', 'pause', 'raw',
                'repeat', 'saturation',
                'set', 'to', 'units', 'while', 'with', 'wait',
                'zone')), Keyword.Reserved),
            (r'.+', Text)
        ]
    }
