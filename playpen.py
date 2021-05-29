#!/usr/bin/python
############################################################################################
#
# playpen.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Work area to get various components up and running.
#
# To Do - test if this still works under python3
#
############################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
############################################################################################

import sys
from dx.spot_processing import Station, Spot, WWV, Comment, ChallengeData
from pprint import pprint
import hint
import webbrowser

############################################################################################

dx_station = Station("W1AW")
print(dx_station)
pprint(vars(dx_station))
h = hint.oh_canada(dx_station)
print('hint=',h)

link='https://www.qrz.com/db/'+dx_station.call
webbrowser.open(link, new=2)
sys.exit(0)

dx_station = Station("AA2IL")
print(dx_station)
pprint(vars(dx_station))

qth=''
h = hint.commie_fornia(dx_station.cqz,qth)
print('hint=',h)

qth='S'
h = hint.commie_fornia(dx_station.cqz,qth)
print('hint=',h)

qth='SB'
h = hint.commie_fornia(dx_station.cqz,qth)
print('hint=',h)

