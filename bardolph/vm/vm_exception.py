class VmException(Exception):
    def __init__(self, msg):
        super().__init__('Execution stopped: {}'.format(msg))
