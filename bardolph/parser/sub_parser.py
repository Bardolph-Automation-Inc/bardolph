from bardolph.vm.vm_codes import Register

class SubParser:
    def __init__(self, parser):
        self.parser = parser

    @property
    def current_token(self):
        return self.parser.current_token

    @property
    def code_gen(self):
        return self.parser._code_gen

    @property
    def context(self):
        return self.parser._context

    @property
    def current_float(self):
        return self.parser._current_float()

    @property
    def current_str(self):
        return self.parser._current_str()

    @property
    def current_reg(self):
        return self.parser._current_reg()

    @property
    def current_literal(self):
        return self.parser._current_literal()

    def next_token(self):
        return self.parser.next_token()

    def rvalue(self, dest=Register.RESULT, code_gen=None):
        return self.parser._rvalue(dest, code_gen)

    def at_rvalue(self):
        return self.parser._at_rvalue()

    def trigger_error(self, msg):
        return self.parser.trigger_error(msg)

    def token_error(self, fmt):
        return self.parser.token_error(fmt)
