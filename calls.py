############################################################################################
#
# calls.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for random callsigns practice.
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
from random import random
from rig_io.ft_tables import SST_SECS
from default import DEFAULT_KEYING

############################################################################################

VERBOSITY=0

############################################################################################

# Keying class for SST mini tests  - inherits base class
class RANDOM_CALLS_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'SST','K1USNSST*.txt')


    # Routient to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL]'}
        MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] ee [LOG]'}
        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU '}
        MACROS[6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[6+12]  = {'Label' : '? '        , 'Text' : '? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        
        MACROS[8]     = {'Label' : ' '          , 'Text' : ' '}
        MACROS[9]     = {'Label' : ' '          , 'Text' : ' '}
        MACROS[10]    = {'Label' : ' '          , 'Text' : ' '}
        MACROS[11]    = {'Label' : ' '          , 'Text' : ' '}

        return MACROS

    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        return ' '

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        if iopt==1:
            
            done = True
            return done

        else:

            self.call = call
            txt2  = ' '
            return txt2
            
    # Error checking
    def error_check(self):
        P=self.P

        call2 = P.gui.get_call().upper()
        match = self.call==call2

        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            txt2='Call sent:'+self.call+'\t- received:'+call2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
            


    # Specific contest exchange for SST
    def enable_boxes(self,gui):

        gui.contest=True
        gui.hide_all()

        # Indicate which macro to fire if return key is pressed while in each entry bos
        self.macros=[1,None,2]

        gui.boxes=[gui.call]
        gui.boxes.append(gui.name)
        gui.boxes.append(gui.qth)
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui
        
        call=gui.get_call().upper()
        valid = len(call)>=3

        exch    = ''
        exch_out = ''

        qso2={}
        
        return exch,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui


    # Hint insertion
    def insert_hint(self,h):

        gui=self.P.gui

