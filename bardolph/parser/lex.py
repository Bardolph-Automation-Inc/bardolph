import re

from .token_types import TokenTypes

token_regex = re.compile(r'"(.*?)"|\s+|\w+|#.*\n?')
word_regex = re.compile(r"\w+")
int_regex = re.compile(r"^\d+$")

class Lex:
    def __init__(self, input_string):
        self.tokens = token_regex.finditer(input_string)
        self.line_num = 1
    
    def next_token(self):
        token_type = TokenTypes.space

        while token_type == TokenTypes.space:
            match = next(self.tokens, None)
            if match == None:
                token = ''
                token_type = TokenTypes.eof
            else:
                token = match.group(0)
                self.line_num += token.count("\n")                
                if token[0] == '#' or not word_regex.search(token):
                    token_type = TokenTypes.space
                else:
                    if token[0] == '"':
                        token = token[1:-1]
                        token_type = TokenTypes.literal
                    elif int_regex.search(token):
                        token_type = TokenTypes.integer
                    elif token == 'and':
                        token_type = TokenTypes.and_operand
                    else: 
                        token_type = TokenTypes.__members__.get(
                            token, TokenTypes.unknown)

        return (token_type, token)       
