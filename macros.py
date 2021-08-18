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
#from rig_io.ft_tables import MY_CALL

############################################################################################

# Valid precidences for ARRL SS
PRECS='QSABUMS'

# Table of pre-defined macros
MACROS = OrderedDict()
CONTEST = OrderedDict()

Key='Default'
MACROS[Key] = OrderedDict()
MACROS[Key][0]  = {'Label' : 'CQ'      , 'Text' : 'CQ CQ CQ DE [MYCALL] [MYCALL] K '}
MACROS[Key][1]  = {'Label' : '[MYCALL]' , 'Text' : '[MYCALL] '}
MACROS[Key][2]  = {'Label' : 'Reply'   , 'Text' : 'RTU [RST] [MYSTATE] '}
MACROS[Key][3]  = {'Label' : 'OP'      , 'Text' : 'OP [MYNAME] [MYNAME] '}
MACROS[Key][4]  = {'Label' : 'QTH'     , 'Text' : 'QTH [MYSTATE] [MYSTATE] '}
MACROS[Key][5]  = {'Label' : '73'      , 'Text' : '73 '}
MACROS[Key][6]  = {'Label' : 'BK'      , 'Text' : 'BK '}
MACROS[Key][7]  = {'Label' : 'Call?'   , 'Text' : '[CALL]? '}
MACROS[Key][8]  = {'Label' : 'LOG it'  , 'Text' : '[LOG]'}
MACROS[Key][9]  = {'Label' : 'RST  '   , 'Text' : '[RST]'}
MACROS[Key][10] = {'Label' : 'V    '   , 'Text' : 'V'}
MACROS[Key][11] = {'Label' : 'Test '   , 'Text' : 'VVV [+10]VVV[-10] VVV'}
CONTEST[Key]=False

Key='Satellite_QSO'
MACROS[Key] = OrderedDict()
MACROS[Key][0]  = {'Label'    : 'CQ'          , 'Text' : 'CQ CQ CQ DE [MYCALL] [MYCALL] K '}
MACROS[Key][0+12]  = {'Label' : 'QRS '        , 'Text' : 'QRS PSE QRS '}
MACROS[Key][1]     = {'Label' : 'Reply'       , 'Text' : '[CALL] TU [RST] [MYGRID] [MYGRID] BK'}
MACROS[Key][1+12]  = {'Label' : 'Long'        , 'Text' : '[CALL] TU FER THE CALL [RST] [MYGRID] [MYGRID] OP [MYNAME] [MYNAME] BK'}
MACROS[Key][2]     = {'Label' : 'TU/QRZ?'     , 'Text' : '[CALL_CHANGED] R73 QRZ? [MYCALL] [LOG]'}
MACROS[Key][2+12]  = {'Label' : 'TU/QRZ?'     , 'Text' : '[CALL_CHANGED] MNY TNX FER QSO ES 73 QRZ? [MYCALL] [LOG]'}
MACROS[Key][3]     = {'Label' : 'Call?'       , 'Text' : '[CALL]? '}
MACROS[Key][3+12] = {'Label' : 'CALL? '       , 'Text' : 'CALL? '}

MACROS[Key][4]     = {'Label' : 'de [MYCALL]' , 'Text' : '[CALL] DE [MYCALL] {MYCALL]'}
MACROS[Key][4+12]  = {'Label' : '[MYCALL]'    , 'Text' : '[CALL] '}
MACROS[Key][5]     = {'Label' : 'S&P Reply'   , 'Text' : 'RR TU [RST] [MYGRID] [MYGRID] BK'}
MACROS[Key][5+12]  = {'Label' : 'S&P 2x'      , 'Text' : 'R TU FER RPRT UR [RST} IN [MYGRID] [MYGRID] OP {MYNAME] [MYNAME] BK'}
MACROS[Key][6]     = {'Label' : 'AGN?'        , 'Text' : 'AGN? '}
MACROS[Key][6+12]  = {'Label' : '? '          , 'Text' : '? '}
MACROS[Key][7]     = {'Label' : 'Log QSO'     , 'Text' : '[LOG] '}

MACROS[Key][8]     = {'Label' : 'OP'          , 'Text' : 'OP [MYNAME] [MYNAME] '}
MACROS[Key][9]     = {'Label' : 'QTH'         , 'Text' : 'QTH [MYSTATE] [MYSTATE] '}
MACROS[Key][10]    = {'Label' : '73'          , 'Text' : '73 GL'}
MACROS[Key][10+1]  = {'Label' : '73'          , 'Text' : 'MNY TNX FER FB QSO 73 HPE CU AGAN '}
MACROS[Key][11]    = {'Label' : '73'          , 'Text' : '73 GL'}
MACROS[Key][12]    = {'Label' : 'BK'          , 'Text' : 'BK '}

CONTEST[Key]=False

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

Key='ARRL Field Day'
MACROS[Key] = OrderedDict()
MACROS[Key][0]     = {'Label' : 'CQ'        , 'Text' : 'CQ FD [MYCALL] '}
MACROS[Key][0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
#MACROS[Key][1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [MYCAT] [MYCAT] [MYSEC] [MYSEC] '}
MACROS[Key][1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [MYCAT] [MYSEC] '}
MACROS[Key][2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] R73 FD [MYCALL] [LOG]'}
MACROS[Key][3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
#MACROS[Key][3+12]  = {'Label' : '?'          , 'Text' : '? '}
MACROS[Key][3+12] = {'Label' : 'CALL? '     , 'Text' : 'CALL? '}

MACROS[Key][4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
MACROS[Key][4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
MACROS[Key][5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [MYCAT] [MYSEC]'}
MACROS[Key][5+12]  = {'Label' : 'S&P 2x'    , 'Text' : '[MYCAT] [MYCAT] [MYSEC] [MYSEC]'}
MACROS[Key][6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
MACROS[Key][6+12]  = {'Label' : '? '        , 'Text' : '? '}
MACROS[Key][7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}

MACROS[Key][8]     = {'Label' : 'Cat 2x'    , 'Text' : '[MYCAT] [MYCAT] '}
MACROS[Key][9]     = {'Label' : 'Sec 2x'    , 'Text' : '[MYSEC] [MYSEC] '}
MACROS[Key][10]    = {'Label' : 'NR?  '     , 'Text' : 'NR? '}
MACROS[Key][11]    = {'Label' : 'QTH? '     , 'Text' : 'SEC? '}
MACROS[Key][11+12] = {'Label' : 'CALL? '     , 'Text' : 'CALL? '}
CONTEST[Key]=True

Key='ARRL VHF'
MACROS[Key] = OrderedDict()
MACROS[Key][0]     = {'Label' : 'CQ'        , 'Text' : 'CQ TEST [MYCALL] '}
MACROS[Key][0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
MACROS[Key][1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [MYGRID] '}
MACROS[Key][2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] R73 [MYCALL] TEST [LOG]'}
MACROS[Key][3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
#MACROS[Key][3+12]  = {'Label' : '?'         , 'Text' : '? '}
MACROS[Key][3+12] = {'Label' : 'CALL? '     , 'Text' : 'CALL? '}

MACROS[Key][4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
MACROS[Key][4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
MACROS[Key][5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [MGRID] [MYGRID]'}
MACROS[Key][5+12]  = {'Label' : 'S&P 2x'    , 'Text' : '[MYGRID] [MYGRID] '}
MACROS[Key][6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
MACROS[Key][6+12]  = {'Label' : '? '        , 'Text' : '? '}
MACROS[Key][7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}

MACROS[Key][8]     = {'Label' : 'Grid 2x'   , 'Text' : '[MYGRID] [MYGRID] '}
MACROS[Key][9]     = {'Label' : 'Grid 2x'   , 'Text' : '[MYGRID] [MYGRID] '}
MACROS[Key][10]    = {'Label' : 'NR?  '     , 'Text' : 'NR? '}
MACROS[Key][11]    = {'Label' : 'QTH? '     , 'Text' : 'SEC? '}
MACROS[Key][11+12] = {'Label' : 'CALL? '    , 'Text' : 'CALL? '}
CONTEST[Key]=True

Key='NAQP'
MACROS[Key] = OrderedDict()
#MACROS[Key][0]     = {'Label' : 'CQ'        , 'Text' : 'CQ NAQP [MYCALL] CQ '}
MACROS[Key][0]     = {'Label' : 'CQ'        , 'Text' : 'CQ NA [MYCALL]'}
MACROS[Key][0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
MACROS[Key][1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [MYNAME] [MYSTATE] '}
MACROS[Key][2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] R73 [MYCALL] NA [LOG]'}
MACROS[Key][2+12]  = {'Label' : 'NIL'       , 'Text' : 'NIL '}
MACROS[Key][3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
MACROS[Key][3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}

MACROS[Key][4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
MACROS[Key][4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
MACROS[Key][5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [MYNAME] [MYSTATE]'}
MACROS[Key][5+12]  = {'Label' : 'S&P 2x'    , 'Text' : '[MYNAME] [MYNAME] [MYSTATE] [MYSTATE]'}
MACROS[Key][6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
MACROS[Key][6+12]  = {'Label' : '? '        , 'Text' : '? '}
MACROS[Key][7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}

MACROS[Key][8]     = {'Label' : 'Name 2x'   , 'Text' : '[MYNAME] [MYNAME] '}
MACROS[Key][9]     = {'Label' : 'State 2x'  , 'Text' : '[MYSTATE] [MYSTATE] '}
MACROS[Key][10]    = {'Label' : 'NAME?  '   , 'Text' : 'NAME? '}
MACROS[Key][11]    = {'Label' : 'QTH? '     , 'Text' : 'QTH? '}
CONTEST[Key]=True

Key='SST'
MACROS[Key] = OrderedDict()
MACROS[Key][0]     = {'Label' : 'CQ'        , 'Text' : 'CQ SST [MYCALL] '}
MACROS[Key][0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
MACROS[Key][1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [MYNAME] [MYSTATE] '}
MACROS[Key][1+12]  = {'Label' : 'Reply'     , 'Text' : '[CALL] TNX AGN [MYNAME] [MYSTATE] '}
MACROS[Key][2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] [GDAY] [NAME] 73 SST [MYCALL] [LOG]'}
MACROS[Key][2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] FB [NAME] GL EE'}
MACROS[Key][3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
MACROS[Key][3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}

MACROS[Key][4]     = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
MACROS[Key][4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
MACROS[Key][5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [NAME] [MYNAME] [MYSTATE]'}
MACROS[Key][5+12]  = {'Label' : 'S&P Reply' , 'Text' : 'TU [MYNAME] [MYSTATE]'}
MACROS[Key][6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
MACROS[Key][6+12]  = {'Label' : '? '        , 'Text' : '? '}
MACROS[Key][7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}

MACROS[Key][8]     = {'Label' : 'Name 2x'   , 'Text' : '[MYNAME] [MYNAME] '}
MACROS[Key][9]     = {'Label' : 'State 2x'  , 'Text' : '[MYSTATE] [MYSTATE] '}
MACROS[Key][10]    = {'Label' : 'NAME?  '   , 'Text' : 'NAME? '}
MACROS[Key][11]    = {'Label' : 'QTH? '     , 'Text' : 'QTH? '}
CONTEST[Key]=True

Key='CWops'
MACROS[Key] = OrderedDict()
MACROS[Key][0]     = {'Label' : 'CQ'        , 'Text' : 'CQ CWT [MYCALL] '}
MACROS[Key][0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
MACROS[Key][1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] [MYNAME] [MYSTATE] '}
MACROS[Key][2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] RTU CWT [MYCALL] [LOG]'}
MACROS[Key][2+12]  = {'Label' : 'NIL'       , 'Text' : 'NIL '}
MACROS[Key][3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
MACROS[Key][3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}

MACROS[Key][4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
MACROS[Key][4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
MACROS[Key][5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [MYNAME] [MYSTATE]'}
MACROS[Key][5+12]  = {'Label' : 'S&P 2x'    , 'Text' : '[MYNAME] [MYNAME] [MYSTATE] [MYSTATE]'}
MACROS[Key][6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
MACROS[Key][6+12]  = {'Label' : '? '        , 'Text' : '? '}
MACROS[Key][7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}

MACROS[Key][8]     = {'Label' : 'Name 2x'   , 'Text' : '[MYNAME] [MYNAME] '}
MACROS[Key][9]     = {'Label' : 'State 2x'  , 'Text' : '[MYSTATE] [MYSTATE] '}
MACROS[Key][10]    = {'Label' : 'NAME?  '   , 'Text' : 'NAME? '}
MACROS[Key][11]    = {'Label' : 'NR?'       , 'Text' : 'NR? '}
CONTEST[Key]=True

Key='CQ_WPX'
MACROS[Key] = OrderedDict()
MACROS[Key][0]     = {'Label' : 'CQ'        , 'Text' : 'CQ TEST [MYCALL] '}
MACROS[Key][0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
MACROS[Key][1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU 5NN [SERIAL] '}
MACROS[Key][2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] R73 [MYCALL] TEST [LOG]'}
MACROS[Key][3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
MACROS[Key][3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}

MACROS[Key][4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
MACROS[Key][4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
MACROS[Key][5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU 5NN [SERIAL]'}
MACROS[Key][5+12]  = {'Label' : 'S&P 2x'    , 'Text' : 'TU 5NN [SERIAL] [SERIAL]'}
MACROS[Key][6]     = {'Label' : '?'         , 'Text' : '? '}
MACROS[Key][6+12]  = {'Label' : 'AGN? '     , 'Text' : 'AGN? '}
MACROS[Key][7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}

MACROS[Key][8]     = {'Label' : 'Serial 2x' , 'Text' : '[-2][SERIAL] [SERIAL][+2]'}
MACROS[Key][9]     = {'Label' : 'NR?'       , 'Text' : 'NR? '}
MACROS[Key][10]    = {'Label' : '-'         , 'Text' : ' '}
MACROS[Key][11]    = {'Label' : '-'         , 'Text' : ' '}
CONTEST[Key]=True

Key='IARU HF'
MACROS[Key] = OrderedDict()
MACROS[Key][0]     = {'Label' : 'CQ'        , 'Text' : 'CQ TEST [MYCALL] '}
MACROS[Key][0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
MACROS[Key][1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU 5NN [MYITUZ] '}
MACROS[Key][2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] R73 [MYCALL] QRZ? [LOG]'}
MACROS[Key][3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
MACROS[Key][3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}

MACROS[Key][4]     = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
MACROS[Key][4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
MACROS[Key][5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU 5NN [MYITUZ]'}
MACROS[Key][5+12]  = {'Label' : 'S&P 2x'    , 'Text' : '[MYITUZ] [MYITUZ]'}
MACROS[Key][6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
MACROS[Key][6+12]  = {'Label' : '? '        , 'Text' : '? '}
MACROS[Key][7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}

MACROS[Key][8]     = {'Label' : 'Zone 2x'   , 'Text' : '[MYITUZ] [MYITUZ] '}
MACROS[Key][9]     = {'Label' : 'Zone 2x'   , 'Text' : '[MYITUZ] [MYITUZ] '}
MACROS[Key][10]    = {'Label' : 'NR?'       , 'Text' : 'NR? '}
MACROS[Key][11]    = {'Label' : 'NR?'       , 'Text' : 'NR? '}
CONTEST[Key]=True

Key='Sprint'
MACROS[Key] = OrderedDict()
MACROS[Key][0]     = {'Label' : 'CQ'        , 'Text' : 'CQ NA [MYCALL] '}
MACROS[Key][1]     = {'Label' : 'Reply1'    , 'Text' : '[CALL] [MYCALL] [SERIAL] [MYNAME] [MYSTATE] '}
MACROS[Key][1+12]  = {'Label' : 'QSY -1'    , 'Text' : '[QSY-1] '}
MACROS[Key][2]     = {'Label' : 'TU/QSY'    , 'Text' : '[LOG] [CALL_CHANGED] TU '}
MACROS[Key][2+12]  = {'Label' : 'QSY +1'    , 'Text' : '[QSY+1] '}

MACROS[Key][4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
MACROS[Key][3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
MACROS[Key][3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}

MACROS[Key][5]     = {'Label' : 'S&P Reply' , 'Text' : '[CALL] [SERIAL] [MYNAME] [MYSTATE] [MYCALL]'}
MACROS[Key][6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
MACROS[Key][6+12]  = {'Label' : '? '        , 'Text' : '? '}
MACROS[Key][7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
MACROS[Key][7+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}

MACROS[Key][8]     = {'Label' : 'Call?'    , 'Text' : 'CALL? '}
MACROS[Key][8+12]  = {'Label' : '[MYCALL] 2x' , 'Text' : '[MYCALL] [MYCALL] '}
MACROS[Key][9]     = {'Label' : 'NR?'      , 'Text' : 'NR? '}
MACROS[Key][9+12]  = {'Label' : 'Serial 2x', 'Text' : '[SERIAL] [SERIAL] '}
MACROS[Key][10]    = {'Label' : 'NAME?'    , 'Text' : 'NAME? '}
MACROS[Key][10+12] = {'Label' : 'Name 2x'  , 'Text' : '[MYNAME] [MYNAME] '}
MACROS[Key][11]    = {'Label' : 'QTH?'     , 'Text' : 'QTH? '}
MACROS[Key][11+12] = {'Label' : 'State 2x' , 'Text' : '[MYSTATE] [MYSTATE] '}
CONTEST[Key]=True

Key='ARRL CW SS'
MACROS[Key] = OrderedDict()
MACROS[Key][0]     = {'Label' : 'CQ'        , 'Text' : 'CQ SS [MYCALL] '}
MACROS[Key][0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
MACROS[Key][1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [SERIAL] [MYPREC] [MYCALL] [MYCHECK] [MYSEC] '}
MACROS[Key][2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] 73 de [MYCALL] QRZ? [LOG]'}
MACROS[Key][3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
MACROS[Key][3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}

MACROS[Key][4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
MACROS[Key][4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
MACROS[Key][5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [SERIAL] [MYPREC] [MYCALL] [MYCHECK] [MYSEC] '}
MACROS[Key][6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
MACROS[Key][6+12]  = {'Label' : '? '        , 'Text' : '? '}
MACROS[Key][7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}

MACROS[Key][8]     = {'Label' : 'NR?'      , 'Text' : 'NR? '}
MACROS[Key][8+12]  = {'Label' : 'Serial 2x', 'Text' : '[SERIAL] [SERIAL] '}
MACROS[Key][9]     = {'Label' : 'Prec?'    , 'Text' : 'PREC? '}
MACROS[Key][9+12]  = {'Label' : 'Prec 2x'  , 'Text' : '[MYPREC] [MYPREC] '}
MACROS[Key][10]    = {'Label' : 'Check?'   , 'Text' : 'CHK? '}
MACROS[Key][10+12] = {'Label' : 'Check 2x' , 'Text' : '[MYCHECK] [MYCHECK] '}
MACROS[Key][11]    = {'Label' : 'Sec?    ' , 'Text' : 'SEC? '}
MACROS[Key][11+12] = {'Label' : 'Sec 2x'   , 'Text' : '[MYSEC] [MYSEC] '}
CONTEST[Key]=True

Key='Cal QP'
MACROS[Key] = OrderedDict()
MACROS[Key][0]     = {'Label' : 'CQ'        , 'Text' : 'CQ CQP [MYCALL] '}
MACROS[Key][0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
MACROS[Key][1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [SERIAL] [MYCOUNTY] '}
MACROS[Key][2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] R73 CQP [MYCALL] [LOG]'}
MACROS[Key][3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
MACROS[Key][3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}

MACROS[Key][4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
MACROS[Key][4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
MACROS[Key][5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [SERIAL] [MYCOUNTY] '}
MACROS[Key][6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
MACROS[Key][6+12]  = {'Label' : '? '        , 'Text' : '? '}
MACROS[Key][7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}

MACROS[Key][8]     = {'Label' : 'NR 2x'    , 'Text' : '[SERIAL] [SERIAL] '}
MACROS[Key][9]     = {'Label' : 'My QTH 2x' , 'Text' : '[MYCOUNTY] [MYCOUNTY] '}
MACROS[Key][10]    = {'Label' : 'NR?'      , 'Text' : 'NR? '}
MACROS[Key][11]    = {'Label' : 'QTH? '    , 'Text' : 'QTH? '}
CONTEST[Key]=True

Key='ARRL 10m'
MACROS[Key] = OrderedDict()
MACROS[Key][0]     = {'Label' : 'CQ'        , 'Text' : 'CQ TEST [MYCALL] '}
MACROS[Key][0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
MACROS[Key][1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU 5NN [MYSTATE] '}
MACROS[Key][2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] R73 TEST [MYCALL] [LOG]'}
MACROS[Key][3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
MACROS[Key][3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}

MACROS[Key][4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
MACROS[Key][4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
MACROS[Key][5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU 5NN [MYSTATE] '}
MACROS[Key][6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
MACROS[Key][6+12]  = {'Label' : '? '        , 'Text' : '? '}
MACROS[Key][7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}

MACROS[Key][8]     = {'Label' : ' '     , 'Text' : ' '}
MACROS[Key][9]     = {'Label' : 'My QTH 2x' , 'Text' : '[MYSTATE] [MYSTATE] '}
MACROS[Key][10]    = {'Label' : ' '       , 'Text' : ' '}
MACROS[Key][11]    = {'Label' : 'QTH? '     , 'Text' : 'QTH? '}
CONTEST[Key]=True

Key='CQ WW'
MACROS[Key] = OrderedDict()
MACROS[Key][0]    = {'Label' : 'CQ'       , 'Text' : 'CQ WW [MYCALL] '}
MACROS[Key][0+12] = {'Label' : 'QRS '     , 'Text' : 'QRS PSE QRS '}
MACROS[Key][1]    = {'Label' : 'Reply'    , 'Text' : '[CALL] TU 5NN [MYCQZ] '}
MACROS[Key][2]    = {'Label' : 'TU/QRZ?'  , 'Text' : '[CALL_CHANGED] R73 WW [MYCALL] [LOG]'}
MACROS[Key][3]    = {'Label' : 'Call?'    , 'Text' : '[CALL]? '}
MACROS[Key][3+12] = {'Label' : 'Call?'    , 'Text' : 'CALL? '}

MACROS[Key][4]    = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
MACROS[Key][4+12] = {'Label' : 'His Call' , 'Text' : '[CALL] '}
MACROS[Key][5]    = {'Label' : 'S&P Reply', 'Text' : 'TU 5NN [MYCQZ] '}
MACROS[Key][6]    = {'Label' : 'AGN?'     , 'Text' : 'AGN? '}
MACROS[Key][6+12] = {'Label' : '? '       , 'Text' : '? '}
MACROS[Key][7]    = {'Label' : 'Log QSO'  , 'Text' : '[LOG] '}

MACROS[Key][8]    = {'Label' : 'Zone 2x'  , 'Text' : '[MYCQZ] [MYCQZ '}
MACROS[Key][9]    = {'Label' : 'NR?'      , 'Text' : 'NR? '}
MACROS[Key][10]   = {'Label' : 'B4'       , 'Text' : '[CALL] B4'}
MACROS[Key][11]   = {'Label' : 'Nil'      , 'Text' : 'NIL'}
CONTEST[Key]=True

Key='ARRL DX'
MACROS[Key] = OrderedDict()
MACROS[Key][0]  = {'Label' : 'CQ'        , 'Text' : 'CQ [MYCALL] TEST'}
MACROS[Key][1]  = {'Label' : 'Reply'     , 'Text' : '[CALL] TU 5NN [MYSTATE] '}
MACROS[Key][2]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] R73 [MYCALL] TEST [LOG]'}
MACROS[Key][3]  = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}

MACROS[Key][4]  = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
MACROS[Key][5]  = {'Label' : 'S&P Reply' , 'Text' : 'TU 5NN [MYSTATE]'}
MACROS[Key][6]  = {'Label' : '?'         , 'Text' : '??'}
MACROS[Key][7]  = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}

MACROS[Key][8]  = {'Label' : '[MYCALL] 2x'  , 'Text' : 'DE [MYCALL] [MYCALL]'}
MACROS[Key][9]  = {'Label' : 'State 2x'  , 'Text' : '[MYSTATE] [MYSTATE] '}
MACROS[Key][10] = {'Label' : 'NR?'       , 'Text' : 'NR? '}
MACROS[Key][11] = {'Label' : '73'        , 'Text' : '73 '}

CONTEST[Key]=True

Key='Stew_Perry'
MACROS[Key] = OrderedDict()
MACROS[Key][0]  = {'Label' : 'CQ'      , 'Text' : 'CQ SP [MYCALL] CQ '}
MACROS[Key][1]  = {'Label' : 'Reply'   , 'Text' : '[CALL] TU [MYGRID] [MYGRID] [CALL] '}
MACROS[Key][2]  = {'Label' : 'TU/QRZ?' , 'Text' : '[CALL] TU 73 de [MYCALL] QRZ? '}
MACROS[Key][3]  = {'Label' : 'AGN?'    , 'Text' : 'AGN? '}
MACROS[Key][4]  = {'Label' : '[MYCALL]' , 'Text' : '[MYCALL] '}
MACROS[Key][5]  = {'Label' : 'Reply 1' , 'Text' : 'TU [MYGRID] '}
MACROS[Key][6]  = {'Label' : 'Reply 2' , 'Text' : 'TU [MYGRID] [MYGRID]'}
MACROS[Key][7]  = {'Label' : 'Grid 2x' , 'Text' : '[MYGRID] [MYGRID] '}
MACROS[Key][8]  = {'Label' : 'Agn?  '  , 'Text' : 'AGN? '}
MACROS[Key][9]  = {'Label' : 'GRID? '  , 'Text' : 'GRID? '}
MACROS[Key][10] = {'Label' : '      '  , 'Text' : ' '}
MACROS[Key][11] = {'Label' : '      '  , ' ' : ' '}
CONTEST[Key]=True



# Sprints:
""" If you call CQ, you should send your report as follows:

HIS CALLSIGN  -  YOUR CALLSIGN   -  NUMBER  -  NAME  -  STATE

Example:

K5ZD W4AN 357 Bill GA

If you find a station S&Ping, then at the completion of the QSO the frequency will be yours.  In this case, you will want to send your callsign last so people on frequency know you are the person to call.

Example:

K5ZD 357 Bill GA W4AN

This is simply done by programming different CW memories with different messages.

Also remember, you MUST send the callsign of the station you are working and your callsign with each QSO.  

For RTTY, do this:

K6LL: NA K6LL K6LL CQ
AA3B: AA3B AA3B
K6LL: AA3B K6LL 132 DAVE AZ
AA3B: K6LL 136 BUD PA AA3B
K6LL: TU
(K6LL must now QSY)
K0AD: K0AD K0AD
AA3B: K0AD AA3B 137 BUD PA
K0AD : AA3B 119 AL MN K0AD
AA3B: R
(AA3B must now QSY)
K0AD: NA K0AD K0AD CQ
N6RO: N6RO N6RO

"""
