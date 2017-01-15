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

from __future__ import absolute_import # so we can import 'argparse'

from argparse import ArgumentParser as BaseArgumentParser

class ArgumentParser(BaseArgumentParser):
    """
    Enhanced argument parser.
    
    * Support for flag arguments.
    * Applied patch to fix `this issue <https://bugs.python.org/issue22433>`__.
    """

    def add_flag_argument(self, name, help_true=None, help_false=None, default=False):
        """
        Adds a flag argument as two arguments: ``--my-flag`` and ``--no-my-flag``.
        """

        dest = name.replace('-', '_')

        if default:
            if help_true is not None:
                help_true += ' (default)'
            else:
                help_true = '(default)'
        else:
            if help_false is not None:
                help_false += ' (default)'
            else:
                help_false = '(default)'

        group = self.add_mutually_exclusive_group()
        group.add_argument('--%s' % name, action='store_true', help=help_true)
        group.add_argument('--no-%s' % name, dest=dest, action='store_false', help=help_false)

        self.set_defaults(**{dest: default})

    def _parse_optional(self, arg_string):
        if self._is_positional(arg_string):
            return None

        # if the option string is present in the parser, return the action
        if arg_string in self._option_string_actions:
            action = self._option_string_actions[arg_string]
            return action, arg_string, None

        # if the option string before the "=" is present, return the action
        if '=' in arg_string:
            option_string, explicit_arg = arg_string.split('=', 1)
            if option_string in self._option_string_actions:
                action = self._option_string_actions[option_string]
                return action, option_string, explicit_arg

        # search through all possible prefixes of the option string
        # and all actions in the parser for possible interpretations
        option_tuples = self._get_option_tuples(arg_string)

        # if multiple actions match, the option string was ambiguous
        if len(option_tuples) > 1:
            options = ', '.join(
                [option_string for action, option_string, explicit_arg in option_tuples])
            tup = arg_string, options
            self.error('ambiguous option: %s could match %s' % tup)

        # if exactly one action matched, this segmentation is good,
        # so return the parsed action
        elif len(option_tuples) == 1:
            option_tuple = option_tuples
            return option_tuple

        # if it was not found as an option, but it looks like a negative
        # number, it was meant to be positional
        # unless there are negative-number-like options
        if self._negative_number_matcher.match(arg_string):
            if not self._has_negative_number_optionals:
                return None

        # it was meant to be an optional but there is no such option
        # in this parser (though it might be a valid option in a subparser)
        return None, arg_string, None

    def _is_positional(self, arg_string):
        # if it's an empty string, it was meant to be a positional
        if not arg_string:
            return True

        # if it doesn't start with a prefix, it was meant to be positional
        if not arg_string[0] in self.prefix_chars:
            return True

        # if it's just a single character, it was meant to be positional
        if len(arg_string) == 1:
            return True

        # if it contains a space, it was meant to be a positional
        if ' ' in arg_string and arg_string[0] not in self.prefix_chars:
            return True

        return False
