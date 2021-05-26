#!/usr/bin/python
############################################################################################

# Playpen - J.B.Attili - 2019

# Work area to get various components up and running.

# To Do - test if this works under python3

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

