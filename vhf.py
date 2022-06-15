############################################################################################
#
# vhf.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for ARRL VHF and Stew Perry 160m contests
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
class VHF_KEYING(DEFAULT_KEYING):

    def __init__(self,P,contest_name):
        DEFAULT_KEYING.__init__(self,P,contest_name,'ARRLVHF*.txt')

    # Routine to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ TEST [MYCALL] '}
        MACROS[0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [MYGRID] '}
        MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] R73 [MYCALL] TEST [LOG]'}
        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        #MACROS[3+12]  = {'Label' : '?'         , 'Text' : '? '}
        MACROS[3+12] = {'Label' : 'CALL? '     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [MYGRID] [MYGRID]'}
        MACROS[5+12]  = {'Label' : 'S&P 2x'    , 'Text' : '[MYGRID] [MYGRID] '}
        MACROS[6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[6+12]  = {'Label' : '? '        , 'Text' : '? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        
        MACROS[8]     = {'Label' : 'Grid 2x'   , 'Text' : '[MYGRID] [MYGRID] '}
        MACROS[9]     = {'Label' : 'Grid 2x'   , 'Text' : '[MYGRID] [MYGRID] '}
        MACROS[10]    = {'Label' : 'GRID?  '   , 'Text' : 'GRID? '}
        MACROS[11]    = {'Label' : 'QTH? '     , 'Text' : 'QTH? '}
        
        return MACROS

    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        gridsq = P.MASTER[call]['grid']
        return gridsq

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        grid=HIST[call]['grid']
        
        if iopt==1:
            
            done = len(grid)==4
            return done

        else:

            self.call = call
            self.qth  = grid
            
            txt2   = ' '+grid
            return txt2
            
    # Error checking
    def error_check(self):
        P=self.P

        call2 = P.gui.get_call().upper()
        qth2  = P.gui.get_qth().upper()
        match = self.call==call2 and self.qth==qth2

        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            txt2='Call sent:'+self.call+'\t- received:'+call2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            txt2='Grid sent: '+self.qth+'\t-\treceived: '+qth2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
            

    # Specific contest exchange for ARRL VHF
    def enable_boxes(self,gui):

        gui.contest=True
        gui.hide_all()
        self.macros=[1,2]

        col=0
        cspan=3
        gui.call_lab.grid(column=col,columnspan=cspan)
        gui.call.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.qth_lab.grid(column=col,columnspan=cspan)
        gui.qth.grid(column=col,columnspan=cspan)

        gui.boxes=[gui.call]
        gui.boxes.append(gui.qth)
            
        if not gui.P.NO_HINTS:
            gui.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
            gui.hint.grid(column=7,columnspan=3)
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        call = gui.get_call().upper()
        qth = gui.get_qth().upper()
        valid = len(call)>=3 and len(qth)>=4

        MY_GRID     = self.P.SETTINGS['MY_GRID']
        exch_out = MY_GRID

        qso2={}
        
        return qth,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        gui.qth.delete(0,END)
        gui.qth.insert(0,a[0])

    # Hint insertion
    def insert_hint(self,h=None):

        gui=self.P.gui

        if h==None:
            h = gui.hint.get()
        if type(h) == str:
            h = h.split(' ')
        
        gui.qth.delete(0, END)
        gui.qth.insert(0,h[0])

