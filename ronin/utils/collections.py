
from __future__ import absolute_import # so we can import 'collections'

from collections import OrderedDict

def dedup(values):
    return list(OrderedDict.fromkeys(values))
