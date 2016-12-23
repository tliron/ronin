
from ..libraries import Library
from subprocess import check_output

class SDL(Library):
    def __init__(self):
        super(SDL, self).__init__()
        # run sdl2-config

    def add_to_compile(self, command):
        pass

    def add_to_link(self, command):
        pass

    #output = check_output([ctx.sdl_config_command, flags, self._name]).strip()
