############################################################################################
#
# dx.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for a DX CW contact.
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

from tkinter import END,E,W
from collections import OrderedDict
import sys
from default import DEFAULT_KEYING

############################################################################################

VERBOSITY=0

############################################################################################

# Keying class for ARRL VHF contests
class DX_KEYING(DEFAULT_KEYING):

    def __init__(self,P,contest_name):
        DEFAULT_KEYING.__init__(self,P,contest_name)  #,'RAGCHEW*.txt')

    # Routine to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()

        MACROS[0]  = {'Label' : 'CQ'       , 'Text' : 'CQ DX CQ DX DE [MYCALL] [MYCALL] K '}
        MACROS[1]  = {'Label' : 'CQ Reply' , 'Text' : '[CALL] de [MYCALL] TU FER THE CALL =' \
                      + ' UR [RST] IN [MYSTATE] [MYSTATE] = OP [MYNAME] [MYNAME] BK'}
        MACROS[2]  = {'Label' : 'Reply2'   , 'Text' : 'R FB [NAME], TNX FOR NICE QSO AND CU SOON 73 73 DE [MYCALL] K'}
        MACROS[3]  = {'Label' : 'Dit Dit'  , 'Text' : 'E E QRZ?'}
        
        MACROS[4]  = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
        MACROS[5]  = {'Label' : 'Report'   , 'Text' : 'RTU [NAME] UR [RST] IN [MYQTH] OP [MYNAME] [MYNAME] bk'}
        MACROS[6]  = {'Label' : 'BK'       , 'Text' : 'BK '}
        MACROS[7]  = {'Label' : '     '    , 'Text' : ''}
        
        MACROS[8]  = {'Label' : '73   '    , 'Text' : 'FB [NAME] MNY TNX E HPE CU AGN 73 DE [MYCALL] K'}
        MACROS[9]  = {'Label'   : 'LOG it'      , 'Text' : '[LOG]'}

        MACROS[10] = {'Label'   : 'V    '       , 'Text' : 'V'}
        MACROS[11] = {'Label'   : 'Test '       , 'Text' : 'VVV ^^^^^VVV||||| VVV'}    # This works
        MACROS[11+12] = {'Label'   : 'Test '       , 'Text' : 'VVV [+10]VVV[-10] VVV'}   # This doesn't work - bug in nanoIO code
            
        return MACROS


