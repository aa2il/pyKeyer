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
from macros import MACROS,CONTEST
from cw_keyer import cut_numbers

############################################################################################

VERBOSITY=0

############################################################################################

# Keyin class for working satellites
class SAT_KEYING():

    def __init__(self,P):
        self.P=P

        P.HISTORY = P.HIST_DIR+'master.csv'

        self.contest_name  = 'SATELLITES'
        
        self.macros()

    # Routient to set macros for this contest
    def macros(self):

        Key='Satellite QSO'
        self.Key=Key

        MACROS[Key] = OrderedDict()
        MACROS[Key][0]  = {'Label'    : 'CQ'          , 'Text' : 'CQ CQ CQ DE [MYCALL] [MYCALL] K '}
        MACROS[Key][0+12]  = {'Label' : 'QRS '        , 'Text' : 'QRS PSE QRS '}
        MACROS[Key][1]     = {'Label' : 'Reply'       , 'Text' : '[CALL] TU [RST] [MYGRID] [MYGRID] BK'}
        MACROS[Key][1+12]  = {'Label' : 'Long'        , 'Text' : '[CALL] TU FER THE CALL [RST] [MYGRID] [MYGRID] OP [MYNAME] [MYNAME] BK'}
        MACROS[Key][2]     = {'Label' : 'TU/QRZ?'     , 'Text' : '[CALL_CHANGED] R73 QRZ? [MYCALL] [LOG]'}
        MACROS[Key][2+12]  = {'Label' : 'TU/QRZ?'     , 'Text' : '[CALL_CHANGED] MNY TNX FER QSO ES 73 QRZ? [MYCALL] [LOG]'}
        MACROS[Key][3]     = {'Label' : 'Call?'       , 'Text' : '[CALL]? '}
        MACROS[Key][3+12] = {'Label' : 'CALL? '       , 'Text' : 'CALL? '}
        
        MACROS[Key][4]     = {'Label' : 'de [MYCALL]' , 'Text' : '[CALL] DE [MYCALL] [MYCALL] K'}
        MACROS[Key][4+12]  = {'Label' : '[MYCALL]'    , 'Text' : '[CALL] '}
        MACROS[Key][5]     = {'Label' : 'S&P Reply'   , 'Text' : 'RR TU [RST] [MYGRID] [MYGRID] BK'}
        MACROS[Key][5+12]  = {'Label' : 'S&P 2x'      , 'Text' : 'R TU FER RPRT UR [RST} IN [MYGRID] [MYGRID] OP {MYNAME] [MYNAME] BK'}
        MACROS[Key][6]     = {'Label' : 'AGN?'        , 'Text' : 'AGN? '}
        MACROS[Key][6+12]  = {'Label' : '? '          , 'Text' : '? '}
        MACROS[Key][7]     = {'Label' : 'Log QSO'     , 'Text' : '[LOG] '}
        
        MACROS[Key][8]     = {'Label' : 'OP'          , 'Text' : 'OP [MYNAME] [MYNAME] '}
        MACROS[Key][9]     = {'Label' : 'QTH'         , 'Text' : 'QTH [MYSTATE] [MYSTATE] '}
        MACROS[Key][10]    = {'Label' : '73 Short'    , 'Text' : '73 GL EE'}
        MACROS[Key][10+1]  = {'Label' : '73 Long'     , 'Text' : 'MNY TNX FER FB QSO 73 HPE CU AGAN '}
        MACROS[Key][11]    = {'Label' : '73'          , 'Text' : '73 GL'}
        MACROS[Key][12]    = {'Label' : 'BK'          , 'Text' : 'BK '}
        CONTEST[Key]=False

        
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
            print(call,grid,done)
            return grid,done

        else:

            self.call = call
            self.grid=grid
            
            txt2   = ' '+grid
            return txt2
            
    # Routine to process qso element repeats
    def repeat(self,label,exch2):

        if 'CALL' in label:
            txt2=self.call+' '+self.call
        elif 'GRID?' in label or 'QTH?' in label or  'SEC?' in label:
            txt2=self.grid+' '+self.grid
        else:
            txt2=exch2

        return txt2

    # Error checking
    def error_check(self):
        P=self.P

        call2 = P.gui.get_call().upper()
        grid2 = P.gui.get_exchange().upper()
        match = self.call==call2 and self.grid==grid2

        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            print('Call sent:',self.call,' - received:',call2)
            P.gui.txt.insert(END,'Call sent: '+self.call+' - received: '+call2+'\n')
            
            print('Grid sent:',self.grid,' - received:',grid2)
            P.gui.txt.insert(END,'Grid sent: '+self.grid+' - received: '+grid2+'\n')

            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
            

    # Highlight function keys that make sense in the current context
    def highlight(self,gui,arg):
        
        if arg==0:
            gui.btns1[1].configure(background='green',highlightbackground='green')
            gui.btns1[2].configure(background='green',highlightbackground='green')
            gui.call.focus_set()
        elif arg==1:
            gui.exch.focus_set()
        elif arg==4:
            gui.btns1[5].configure(background='red',highlightbackground= 'red')
            gui.btns1[7].configure(background='red',highlightbackground= 'red')
            gui.btns1[1].configure(background='pale green',highlightbackground=gui.default_color)
            gui.btns1[2].configure(background='pale green',highlightbackground=gui.default_color)
        elif arg==7:
            gui.btns1[1].configure(background='pale green',highlightbackground=gui.default_color)
            gui.btns1[5].configure(background='indian red',highlightbackground=gui.default_color)
            gui.btns1[7].configure(background='indian red',highlightbackground=gui.default_color)
        

    # Specific contest exchange for satellites
    def enable_boxes(self,gui):

        gui.contest=True
        gui.hide_all()

        col=0
        cspan=3
        gui.call_lab.grid(column=col,columnspan=cspan)
        gui.call.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.rst_lab.grid(column=col,columnspan=cspan)
        gui.rst.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.exch_lab.grid(column=col,columnspan=cspan)
        gui.exch.grid(column=col,columnspan=cspan)

        gui.boxes=[gui.call]
        gui.boxes.append(gui.rst)
        gui.boxes.append(gui.exch)
            
        if not gui.P.NO_HINTS:
            gui.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
            gui.hint.grid(column=7,columnspan=3)
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        call = gui.get_call().upper()
        rst  = gui.get_rst().upper()
        exch = gui.get_exchange().upper()
        valid = len(call)>=3 and len(rst)>=2 and len(exch)>=4
        exch = rst+','+exch

        MY_GRID     = self.P.SETTINGS['MY_GRID']
        exch_out = '5NN,'+MY_GRID
        
        return exch,valid,exch_out
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        gui.exch.delete(0,END)
        gui.exch.insert(0,a[0])

    # Hint insertion
    def insert_hint(self,h):

        gui=self.P.gui

        gui.exch.delete(0, END)
        gui.exch.insert(0,h[0])


    # Move on to next entry box & optionally play a macros
    def next_event(self,key,event,n=None):

        gui=self.P.gui

        if n!=None:
            gui.Send_Macro(n) 

        if event.widget==gui.txt:
            #print('txt->call')
            next_widget = gui.call
        else:
            idx=gui.boxes.index(event.widget)
            nn = len(gui.boxes)
            #if idx==nn and key in ['Return','KP_Enter']:
            #    idx2 = idx
            if key in ['Tab','Return','KP_Enter']:
                idx2 = (idx+1) % nn
            elif key=='ISO_Left_Tab':
                idx2 = (idx-1) % nn
            else:
                print('We should never get here!!')
            #print(idx,'->',idx2)
            next_widget = gui.boxes[idx2]

        next_widget.focus_set()
        return next_widget
            
