# -*- coding: utf-8 -*-
# pylint: disable=C0301, R0902, R0903
"""
    Copyright (C) 2023 by Penwywern <gaspard.larrouturou@protonmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import os
import platform

print("")
print("")
print(f"sys path                : {sys.path}")
print("")
print(f"sys executable          : {sys.executable}")
print(f"sys version             : {sys.version_info}")
print(f"sys exec prefix         : {sys.exec_prefix}")
print(f"sys prefix              : {sys.prefix}")
print(f"sys base exec prefix    : {sys.base_exec_prefix}")
print(f"sys base prefix         : {sys.base_prefix}")
print(f"sys executable realpath : {os.path.realpath(sys.executable)}")
print("")
print(f"Platform                : {platform.platform()}")
print("")
print("")