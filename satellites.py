############################################################################################
#
# satellites.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for working satellites.
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
from random import randint
from cw_keyer import cut_numbers
from default import DEFAULT_KEYING

############################################################################################

VERBOSITY=0

############################################################################################

# Keyin class for working satellites
class SAT_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'SATELLITES',None)

    # Routient to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]  = {'Label'    : 'CQ'          , 'Text' : 'CQ CQ CQ DE [MYCALL] [MYCALL] K '}
        MACROS[0+12]  = {'Label' : 'QRS '        , 'Text' : 'QRS PSE QRS '}
        MACROS[1]     = {'Label' : 'Reply'       , 'Text' : '[CALL] TU [RST] [MYGRID] [MYGRID] BK'}
        MACROS[1+12]  = {'Label' : 'Long'        , 'Text' : '[CALL] TU FER THE CALL [RST] [MYGRID] [MYGRID] OP [MYNAME] [MYNAME] BK'}
        MACROS[2]     = {'Label' : 'TU/QRZ?'     , 'Text' : '[CALL_CHANGED] R73 QRZ? [MYCALL] [LOG]'}
        MACROS[2+12]  = {'Label' : 'TU/QRZ?'     , 'Text' : '[CALL_CHANGED] MNY TNX FER QSO ES 73 QRZ? [MYCALL] [LOG]'}
        MACROS[3]     = {'Label' : 'Call?'       , 'Text' : '[CALL]? '}
        MACROS[3+12] = {'Label' : 'CALL? '       , 'Text' : 'CALL? '}

        MACROS[4]     = {'Label' : 'de [MYCALL]' , 'Text' : '[CALL] DE [MYCALL] [MYCALL] K'}
        MACROS[4+12]  = {'Label' : '[MYCALL]'    , 'Text' : '[MY_CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply'   , 'Text' : 'RR TU [RST] [MYGRID] [MYGRID] BK'}
        MACROS[5+12]  = {'Label' : 'S&P 2x'      , 'Text' : 'R TU FER RPRT UR [RST} IN [MYGRID] [MYGRID] OP {MYNAME] [MYNAME] BK'}
        MACROS[6]     = {'Label' : 'AGN?'        , 'Text' : 'AGN? '}
        MACROS[6+12]  = {'Label' : '? '          , 'Text' : '? '}
        MACROS[7]     = {'Label' : 'Log QSO'     , 'Text' : '[LOG] '}
        
        MACROS[8]     = {'Label' : 'OP'          , 'Text' : 'OP [MYNAME] [MYNAME] '}
        MACROS[9]     = {'Label' : 'QTH'         , 'Text' : 'QTH [MYSTATE] [MYSTATE] '}
        MACROS[10]    = {'Label' : '73 Short'    , 'Text' : '73 GL EE'}
        MACROS[10+1]  = {'Label' : '73 Long'     , 'Text' : 'MNY TNX FER FB QSO 73 HPE CU AGAN '}
        MACROS[11]    = {'Label' : '73'          , 'Text' : '73 GL EE'}
        MACROS[12]    = {'Label' : 'BK'          , 'Text' : 'BK '}
        
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
            self.grid=grid

            sig = randint(0, 9)
            self.rst = cut_numbers( 500+10*sig+9 )
            
            txt2   = ' R '+self.rst+' '+grid+' '+grid
            return txt2
            

    # Error checking
    def error_check(self):
        P=self.P

        call2 = P.gui.get_call().upper()
        grid2 = P.gui.get_exchange().upper()
        rst2  = P.gui.get_rst_in().upper()
        match = self.call==call2 and self.grid==grid2 and self.rst==rst2

        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            txt2='Call sent: '+self.call+'\t-\treceived: '+call2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            txt2='RST sent: '+self.rst+'\t-\treceived: '+rst2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            txt2='Grid sent: '+self.grid+'\t-\treceived: '+grid2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
            


    # Specific contest exchange for satellites
    def enable_boxes(self,gui):

        gui.contest=True
        gui.hide_all()
        self.macros=[None,1,None,2]

        col=0
        cspan=3
        gui.call_lab.grid(column=col,columnspan=cspan)
        gui.call.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=1
        gui.rstout_lab.grid(column=col,columnspan=cspan)
        gui.rstout.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=1
        gui.rstin_lab.grid(column=col,columnspan=cspan)
        gui.rstin.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.exch_lab.grid(column=col,columnspan=cspan)
        gui.exch.grid(column=col,columnspan=cspan)

        gui.boxes=[gui.call]
        gui.boxes.append(gui.rstout)
        gui.boxes.append(gui.rstin)
        gui.boxes.append(gui.exch)
            
        if not gui.P.NO_HINTS:
            gui.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
            gui.hint.grid(column=7,columnspan=3)
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        call   = gui.get_call().upper()
        rstin  = gui.get_rst_in().upper()
        rstout = gui.get_rst_out().upper()
        exch   = gui.get_exchange().upper()
        valid  = len(call)>=3 and len(rstin)>0 and len(exch)>0
        exch   = rstin+','+exch

        MY_GRID     = self.P.SETTINGS['MY_GRID']
        exch_out = rstout+','+MY_GRID
        
        return exch,valid,exch_out
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        gui.exch.delete(0,END)
        if len(a)>=2:
            gui.exch.insert(0,a[1])

    # Hint insertion
    def insert_hint(self,h):

        gui=self.P.gui

        gui.exch.delete(0, END)
        gui.exch.insert(0,h[0])

