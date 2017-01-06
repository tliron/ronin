# Copyright 2016-2017 Tal Liron
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from termcolor import colored

def announce(message, color='green'):
    prefix = 'ronin'
    if color:
        prefix = colored(prefix, color)
    print u'%s: %s' % (prefix, message)

def error(message):
    if isinstance(message, BaseException):
        the_type = type(message).__name__
        message = unicode(message)
        if message:
            announce(u'%s: %s' % (the_type, message), 'red')
        else:
            announce(the_type, 'red')
    else:
        announce(u'Error: %s' % message, 'red')

def warning(message):
    announce(u'Warning: %s' % message, 'yellow')
