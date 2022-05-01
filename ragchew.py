############################################################################################
#
# ragchew.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for a regular CW ragchew.
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
class RAGCHEW_KEYING(DEFAULT_KEYING):

    def __init__(self,P,contest_name):
        DEFAULT_KEYING.__init__(self,P,contest_name)  #,'RAGCHEW*.txt')

    # Routine to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label'   : 'CQ'       , 'Text' : 'CQ CQ CQ DE [MYCALL] [MYCALL] K '}
        MACROS[1]     = {'Label'   : 'CQ Reply' , 'Text' : '[CALL] de [MYCALL] = TNX FER THE CALL = ' \
                         + 'UR [RST] [RST] IN [MYQTH] [MYQTH] = NAME IS [MYNAME] [MYNAME] = HW CPY? BK'}
        MACROS[2]     = {'Label'   : 'Meet You' , 'Text' : 'R FB [NAME], SOLID COPY = '\
                         + 'GOOD TO MEET U ='}
        MACROS[2+12]  = {'Label'   : 'Hear U Agn' , 'Text' : 'R FB [NAME], SOLID COPY = '\
                         + 'GOOD TO HEAR U AGN ='}
        MACROS[3]     = {'Label'   : 'BTU'      , 'Text' : 'SO [NAME] BTU DE [MYCALL] > +'}
        MACROS[3+12]  = {'Label'   : 'BK'       , 'Text' : 'HOW? BK '}
        
        MACROS[4]    = {'Label' : 'de [MYCALL]' , 'Text' : '[CALL] de [MYCALL] [MYCALL] '}
        MACROS[4+12] = {'Label' : '[MYCALL]'    , 'Text' : '[MYCALL] '}
        MACROS[5]    = {'Label'   : 'Report'      , 'Text' : 'FB [NAME] SOLID COPY = ' \
                      + 'UR [RST] [RST] IN [MYQTH] [MYQTH] = NAME HR IS [MYNAME] [MYNAME]'}
        MACROS[5+12]  = {'Label'   : 'Report'      , 'Text' : '[GDAY] [NAME] GUD TO MEET U = ' \
                      + 'UR [RST] [RST] IN SAN DIEGO,CA SAN DIEGO, CA = OP [MYNAME] [MYNAME]'}
        MACROS[6]     = {'Label'   : 'Rig'      , 'Text' : 'RIG HR IS YAESU FTDX3K, ABT 100W TO A WIRE BEAM UP 30 FT ='}
        MACROS[6+12]  = {'Label'   : 'Age'      , 'Text' : 'AGE HR IS 59, BEEN A HAM OVER 40 YRS = I AM A RETIRED ELEC ENGINEER ='}
        #                      + 'BEEN HAM SINCE LATE 1970s = I AM A RETIRED ELEC ENGINEER SO REALLY RADIO ='}
        MACROS[7]     = {'Label'   : '?'           , 'Text' : '?'}
        MACROS[7+12]  = {'Label'   : 'AGN ?'       , 'Text' : 'AGN?'}
        
        MACROS[8]     = {'Label'   : '73'          , 'Text' : 'FB [NAME] MNY TNX FOR NICE QSO ES HPE CU AGN = '\
                         + '73 73 % [CALL] DE [MYCALL] K'}
        MACROS[8+12]  = {'Label'   : 'Solid Cpy' , 'Text' : 'R FB [NAME], SOLID COPY = '}
        MACROS[9]     = {'Label'   : 'LOG it'      , 'Text' : '[LOG]'}
        MACROS[10]    = {'Label'   : 'V    '       , 'Text' : 'V'}
        MACROS[11]    = {'Label'   : 'Test '       , 'Text' : 'VVV ^^^^^VVV||||| VVV'}    # This works
        MACROS[11+12] = {'Label'   : 'Test '       , 'Text' : 'VVV [+10]VVV[-10] VVV'}   # This doesn't work - bug in nanoIO code
            
        return MACROS


    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P
        name  = P.MASTER[call]['name']
        state = P.MASTER[call]['state']
        num   = P.MASTER[call]['cwops']
        if len(num)==0:
            num='-'
        if VERBOSITY>0:
            print('RAGCHEW_KEYEING - Hint:',name+' '+state+' '+num)
        return name+' '+state+' '+num


