############################################################################################
#
# vhf.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for ARRL VHF contest
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

# Keyin class for ARRL VHF contests
class VHF_KEYING():

    def __init__(self,P):
        self.P=P

        if P.USE_MASTER:
            P.HISTORY = P.HIST_DIR+'master.csv'
        else:
            #P.HISTORY = HIST_DIR+'ARRLVHFJAN.txt'
            P.HISTORY = HIST_DIR+'ARRLVHF*.txt'

        self.contest_name  = 'ARRL-VHF'
        
        self.macros()

    # Routient to set macros for this contest
    def macros(self):

        Key='ARRL VHF'
        self.Key=Key

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
        

    # Specific contest exchange for ARRL VHF
    def enable_boxes(self,gui):

        gui.contest=True
        gui.hide_all()

        gui.exch_lab.grid(columnspan=3)
        gui.exch.grid(columnspan=3)

        gui.boxes=[gui.call]
        gui.boxes.append(gui.exch)
            
        if not gui.P.NO_HINTS:
            gui.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
            gui.hint.grid(column=7,columnspan=3)
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        call = gui.get_call().upper()
        exch = gui.get_exchange().upper()
        valid = len(call)>=3 and len(exch)>=4

        MY_GRID     = self.P.SETTINGS['MY_GRID']
        exch_out = MY_GRID
        
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
            
