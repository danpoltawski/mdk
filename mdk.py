#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Moodle Development Kit

Copyright (c) 2013 Frédéric Massart - FMCorz.net

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

http://github.com/FMCorz/mdk
"""

import sys
import argparse
import os
import re
from lib.command import CommandRunner
from lib.commands import *
from lib.config import Conf
from lib.tools import process
from version import __version__

C = Conf()

availcmds = [x.replace('Command', '').lower() for x in globals().keys() if x.endswith('Command')]
availaliases = [str(x) for x in C.get('aliases').keys()]
choices = sorted(availcmds + availaliases)

parser = argparse.ArgumentParser(description='Moodle Development Kit', add_help=False)
parser.add_argument('-h', '--help', action='store_true', help='show this help message and exit')
parser.add_argument('-l', '--list', action='store_true', help='list the available commands')
parser.add_argument('-v', '--version', action='store_true', help='displauy the current version')
parser.add_argument('command', metavar='command', nargs='?', help='command to call', choices=choices)
parser.add_argument('args', metavar='arguments', nargs=argparse.REMAINDER, help='arguments of the command')
parsedargs = parser.parse_args()

cmd = parsedargs.command
args = parsedargs.args

# There is no command, what do we do?
if not cmd:
    if parsedargs.version:
        print 'MDK version %s' % __version__
    elif parsedargs.list:
        for c in sorted(availcmds):
            print '  %s' % c
    else:
        parser.print_help()
    sys.exit(0)

# Looking up for an alias
alias = C.get('aliases.%s' % cmd)
if alias != None:
    if alias.startswith('!'):
        cmd = alias[1:]
        i = 0
        # Replace $1, $2, ... with passed arguments
        for arg in args:
            i += 1
            cmd = cmd.replace('$%d' % i, arg)
        # Remove unknown $[0-9]
        cmd = re.sub(r'\$[0-9]', '', cmd)
        result = process(cmd, stdout=None, stderr=None)
        sys.exit(result[0])
    else:
        cmd = alias.split(' ')[0]
        args = alias.split(' ')[1:] + args

# Calling the command
classname = '%sCommand' % (cmd.capitalize())
cls = globals().get(classname)
Cmd = cls(C)
Runner = CommandRunner(Cmd)
Runner.run(args, prog='%s %s' % (os.path.basename(sys.argv[0]), cmd))
