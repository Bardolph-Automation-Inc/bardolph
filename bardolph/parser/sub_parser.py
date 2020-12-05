class SubParser:
    def __init__(self, parser):
        self.parser = parser

    @property
    def current_token(self):
        return self.parser.current_token

    @property
    def current_token_type(self):
        return self.parser.current_token_type

    @property
    def code_gen(self):
        return self.parser._code_gen

    def next_token(self):
        return self.parser.next_token()

    def token_error(self, fmt):
        return self.parser.token_error(fmt)
