
from .utils import host_variant

class Project(object):
    def __init__(self, name=None, version=None, variant=host_variant()):
        self.name = name
        self.version = version
        self.variant = variant
        self.rules = {}

    def __str__(self):
        if self.version and self.variant:
            return '%s v%s (%s)' % (self.name, self.version, self.variant)
        elif self.version and not self.variant:
            return '%s v%s' % (self.name, self.version)
        elif self.variant and not self.version:
            return '%s (%s)' % (self.name, self.variant)
        else:
            return self.name
