import re

from .token_types import TokenTypes


class Lex:
    token_regex = re.compile(r'#.*$|".*?"|\S+') 
    number_regex = re.compile(r'^[0-9]*\.?[0-9]+$')

    def __init__(self, input_string):
        self.lines = iter(input_string.split('\n'))
        self.line_num = 0
        self.tokens = None
        self.next_line()
        
    def next_line(self):
        current_line = next(self.lines, None)
        if current_line is None:
            self.tokens = None
        else:
            self.line_num += 1
            self.tokens = self.token_regex.finditer(current_line)
    
    def next_token(self):
        token_type = None
        while token_type is None:
            match = next(self.tokens, None)
            while match is None:
                self.next_line()
                if self.tokens is None:
                    return (TokenTypes.EOF, '')
                else:
                    match = next(self.tokens, None)
            else:
                token = match.string[match.start():match.end()]
                if token[0] != '#':
                    if token[0] == '"':
                        token = token[1:-1]
                        token_type = TokenTypes.LITERAL
                    elif self.number_regex.search(token):
                        token_type = TokenTypes.NUMBER
                    else: 
                        token_type = TokenTypes.__members__.get(
                            token.upper(), TokenTypes.UNKNOWN)
        
        return (token_type, token)
