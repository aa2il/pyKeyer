############################################################################################
#
# macros.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Pre-programmed macros for 12 function keys (and their shifted varients).
#
# To Do: These should be in a text file instead of hard-coded.
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

from collections import OrderedDict

############################################################################################

# Table of pre-defined macros
MACROS = OrderedDict()
CONTEST = OrderedDict()

Key='Regular_QSO'
MACROS[Key] = OrderedDict()
MACROS[Key][0]  = {'Label'   : 'CQ'       , 'Text' : 'CQ CQ CQ DE [MYCALL] [MYCALL] K '}
MACROS[Key][1]  = {'Label'   : 'CQ Reply' , 'Text' : '[CALL] de [MYCALL] TU FER THE CALL =' \
                   + ' UR [RST] IN [MYQTH] [MYQTH] = NAME IS [MYNAME] [MYNAME] = HW? BK'}
MACROS[Key][2]  = {'Label'   : 'Reply2'   , 'Text' : 'R FB [NAME], SOLID COPY = RIG IS FTDX3K, 100W TO DIPOLE UP 30 FT'}
MACROS[Key][3]  = {'Label'   : 'BTU'      , 'Text' : 'SO [NAME] BTU DE [MYCALL] KN'}
MACROS[Key][4]    = {'Label' : 'de [MYCALL]' , 'Text' : '[CALL] de [MYCALL] [MYCALL] '}
MACROS[Key][4+12] = {'Label' : '[MYCALL]'    , 'Text' : '[MYCALL] '}
MACROS[Key][5]  = {'Label'   : 'Report'   , 'Text' : 'FB [NAME] SOLID COPY = UR [RST] [RST] IN [MYQTH] [MYQTH] = NAME HR IS [MYNAME] [MYNAME]'}
MACROS[Key][6]  = {'Label'   : 'BK'       , 'Text' : 'HOW? BK '}
MACROS[Key][7]  = {'Label'   : '     '    , 'Text' : ''}
MACROS[Key][8]  = {'Label'   : '73   '    , 'Text' : 'FB [NAME] MNY TNX FOR NICE QSO E HPE CU AGN = 73 73 DE [MYCALL] K'}
MACROS[Key][9]  = {'Label'   : '     '    , 'Text' : ''}
MACROS[Key][10] = {'Label'   : 'V    '    , 'Text' : 'V'}
MACROS[Key][11] = {'Label'   : 'Test '    , 'Text' : 'VVV [+10]VVV[-10] VVV'}
CONTEST[Key]=False

Key='DX_QSO'
MACROS[Key] = OrderedDict()
MACROS[Key][0]  = {'Label' : 'CQ'       , 'Text' : 'CQ DX CQ DX DE [MYCALL] [MYCALL] K '}
MACROS[Key][1]  = {'Label' : 'CQ Reply' , 'Text' : '[CALL] de [MYCALL] TU FER THE CALL =' \
                   + ' UR [RST] IN [MYSTATE] [MYSTATE] = OP [MYNAME] [MYNAME] BK'}
MACROS[Key][2]  = {'Label' : 'Reply2'   , 'Text' : 'R FB [NAME], TNX FOR NICE QSO AND CU SOON 73 73 DE [MYCALL] K'}
MACROS[Key][3]  = {'Label' : 'Dit Dit'  , 'Text' : 'E E QRZ?'}
MACROS[Key][4]  = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
MACROS[Key][5]  = {'Label' : 'Report'   , 'Text' : 'RTU [NAME] UR [RST] IN [MYQTH] OP [MYNAME] [MYNAME] bk'}
MACROS[Key][6]  = {'Label' : 'BK'       , 'Text' : 'BK '}
MACROS[Key][7]  = {'Label' : '     '    , 'Text' : ''}
MACROS[Key][8]  = {'Label' : '73   '    , 'Text' : 'FB [NAME] MNY TNX E HPE CU AGN 73 DE [MYCALL] K'}
MACROS[Key][9]  = {'Label' : '     '    , 'Text' : ''}
MACROS[Key][10] = {'Label' : 'V    '    , 'Text' : 'V'}
MACROS[Key][11] = {'Label' : 'Test '    , 'Text' : 'VVV [+10]VVV[-10] VVV'}
CONTEST[Key]=False

