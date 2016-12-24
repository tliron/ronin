
from .utils.platform import host_variant
from .utils.strings import stringify

class Project(object):
    """
    An interrelated set of build rules.
    """
    
    def __init__(self, name=None, version=None, variant=None):
        self.name = name
        self.version = version
        self.variant = variant or (lambda ctx: ctx.get('platform_variant', host_variant()))
        self.rules = {}

    def __str__(self):
        name = stringify(self.name)
        version = stringify(self.version)
        variant = stringify(self.variant)
        if version and variant:
            return '%s v%s (%s)' % (name, version, variant)
        elif version and not variant:
            return '%s v%s' % (name, version)
        elif variant and not version:
            return '%s (%s)' % (name, variant)
        else:
            return name
