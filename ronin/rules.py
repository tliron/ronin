
class Rule(object):
    def __init__(self, command=None):
        self.description = None
        self.command = command
        self.inputs = []
        self.output = None
