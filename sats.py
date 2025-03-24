############################################################################################
#
# satellites.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
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
from utilities import cut_numbers
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
        MACROS[0]     = {'Label' : 'CQ'          , 'Text' : 'CQ CQ CQ DE [MYCALL] [MYCALL] K '}
        MACROS[0+12]  = {'Label' : 'CQ'          , 'Text' : 'CQ CQ CQ DE [MYCALL] [MYCALL] [MYGRID] K '}
        #MACROS[0+12]  = {'Label' : 'QRS '        , 'Text' : 'QRS PSE QRS '}
        MACROS[1]     = {'Label' : 'Reply'       , 'Text' : '[CALL] TU [RST] [MYGRID] [MYGRID] BK'}
        MACROS[1+12]  = {'Label' : 'Long'        , 'Text' : '[CALL] TU FER THE CALL [RST] [MYGRID] [MYGRID] OP [MYNAME] [MYNAME] BK'}
        MACROS[2]     = {'Label' : 'TU/QRZ?'     , 'Text' : '[CALL_CHANGED] RR TNX 73 73 ee [LOG]'}
        MACROS[2+12]  = {'Label' : 'TU/QRZ?'     , 'Text' : '[CALL_CHANGED] TNX FER FB QSO [NAME] 73 73 ee [LOG]'}
        MACROS[3]     = {'Label' : 'Call?'       , 'Text' : '[CALL]? '}
        MACROS[3+12] = {'Label' : 'CALL? '       , 'Text' : 'CALL? '}

        MACROS[4]     = {'Label' : 'de [MYCALL]' , 'Text' : '[CALL] DE [MYCALL] [MYCALL] K'}
        MACROS[4+12]  = {'Label' : '[MYCALL]'    , 'Text' : '[MYCALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply'   , 'Text' : 'RR TU [RST] [MYGRID] [MYGRID] BK'}
        MACROS[5+12]  = {'Label' : 'S&P 2x'      , 'Text' : 'R TU FER RPRT UR [RST} IN [MYGRID] [MYGRID] OP {MYNAME] [MYNAME] BK'}
        MACROS[6]     = {'Label' : 'AGN?'        , 'Text' : 'AGN? '}
        MACROS[6+12]  = {'Label' : '? '          , 'Text' : '? '}
        MACROS[7]     = {'Label' : 'Log QSO'     , 'Text' : '[LOG] '}
        
        MACROS[8]     = {'Label' : 'OP'          , 'Text' : 'OP [MYNAME] [MYNAME] '}
        MACROS[9]     = {'Label' : 'QTH'         , 'Text' : 'QTH [MYSTATE] [MYSTATE] '}
        MACROS[10]    = {'Label' : '73 Short'    , 'Text' : '73 GL EE'}
        MACROS[10+12] = {'Label' : '73 Long'     , 'Text' : 'MNY TNX FER FB QSO 73 HPE CU AGAN '}
        MACROS[11]    = {'Label' : '73'          , 'Text' : '73 GL EE'}
        MACROS[11+12] = {'Label' : 'BK'          , 'Text' : 'BK '}
        
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
        #gui.exch_lab.grid(column=col,columnspan=cspan)
        #gui.exch.grid(column=col,columnspan=cspan)
        gui.qth_lab.grid(column=col,columnspan=cspan)
        gui.qth.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.name_lab.grid(column=col,columnspan=cspan)
        gui.name.grid(column=col,columnspan=cspan)

        col+=cspan
        #gui.qsl.grid(column=col,columnspan=1)
        
        gui.boxes=[gui.call]
        gui.boxes.append(gui.rstout)
        gui.boxes.append(gui.rstin)
        #gui.boxes.append(gui.exch)
        gui.boxes.append(gui.qth)
        gui.boxes.append(gui.name)
            
        if not gui.P.NO_HINTS:
            col+=cspan
            cspan=3
            gui.hint_lab.grid(column=col,columnspan=cspan,sticky=E+W)
            gui.hint.grid(column=col,columnspan=cspan)

        gui.sat_lab.grid()
        gui.sat_SB.grid()
            
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        call   = gui.get_call().upper()
        rstin  = gui.get_rst_in().upper()
        rstout = gui.get_rst_out().upper()
        #exch   = gui.get_exchange().upper()
        qth   = gui.get_qth().upper()
        name   = gui.get_name().upper()
        valid  = len(call)>=3 # and len(rstin)>0 and len(exch)>0
        #exch   = rstin+','+exch+','+name
        exch   = rstin+','+qth+','+name

        #a=exch.split(',')
        #gui.set_qth(a[0])

        MY_GRID     = self.P.SETTINGS['MY_GRID']
        exch_out = rstout+','+MY_GRID

        qso2={}
        
        return exch,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        #gui.exch.delete(0,END)
        #gui.exch.insert(0,a[1])
        
        gui.qth.delete(0,END)
        gui.qth.insert(0,a[0])
        gui.qsl_rcvd.set(0)
        if len(a)>=2:
            gui.name.delete(0,END)
            gui.name.insert(0,a[1])
        if len(a)>=3:
            if a[2]=='Y':
                gui.qsl_rcvd.set(1)

    # Hint insertion
    def insert_hint(self,h=None):

        gui=self.P.gui

        if h==None:
            h = gui.hint.get()
        if type(h) == str:
            h = h.split(' ')
        
        #gui.exch.delete(0, END)
        #gui.exch.insert(0,h[0])
        gui.qth.delete(0, END)
        gui.qth.insert(0,h[0])
        if len(h)>=1:
            gui.name.delete(0, END)
            gui.name.insert(0,h[1])


