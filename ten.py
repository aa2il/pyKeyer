############################################################################################
#
# ten.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for ARRL 10m and Intl DX contests
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
import sys

############################################################################################

VERBOSITY=0

############################################################################################

# Keying class for ARRL 10m and Intl DX contests
class TEN_METER_KEYING():

    def __init__(self,P):
        self.P=P

        P.HISTORY = P.HIST_DIR+'master.csv'

        if P.ARRL_10m:
            self.contest_name  = 'ARRL-10M'
        elif P.ARRL_DX:
            self.contest_name  = 'ARRL-DX'
        else:
            print('Rut row!')
            sys.exit(0)
            
        self.macros()

    # Routient to set macros for this contest
    def macros(self):

        if self.P.ARRL_10m:
            Key='ARRL 10m'
        elif self.P.ARRL_DX:
            Key='ARRL DX'
        self.Key=Key

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


    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        state = P.MASTER[call]['state']
        if state=='':
            # Try deciphering from section info
            sec   = P.MASTER[call]['fdsec']
            state=arrl_sec2state(sec)
        return state
    
    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        state=HIST[call]['state']
        
        if iopt==1:
            
            done = len(state)>0
            return state,done

        else:

            self.call = call
            self.rst = '5NN'
            self.qth = state
            
            txt2  = ' 5NN '+state
            return txt2
            
    # Routine to process qso element repeats
    def repeat(self,label,exch2):

        if 'CALL' in label:
            txt2=self.call+' '+self.call
        elif 'NR?' in label or 'QTH?' in label:
            txt2=self.qth+' '+self.qth
        else:
            txt2=exch2

        return txt2

    # Error checking
    def error_check(self):
        P=self.P

        call2 = P.gui.get_call().upper()
        rst2  = P.gui.get_rst().upper()
        qth2  = P.gui.get_qth().upper()
        match = self.call==call2 and self.rst==rst2 and self.qth==qth2
        
        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            print('Call sent:',self.call,' - received:',call2)
            P.gui.txt.insert(END,'Call sent: '+self.call+' - received: '+call2+'\n')
            
            print('RST sent:',self.rst,' - received:',rst2)
            P.gui.txt.insert(END,'RST sent: '+self.rst+' - received: '+rst2+'\n')

            print('QTH sent:',self.qth,' - received:',qth2)
            P.gui.txt.insert(END,'QTH sent: '+self.qth+' - received: '+qth2+'\n')

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
            gui.qth.focus_set()
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

        gui.rst_lab.grid(columnspan=1,column=4,sticky=E+W)
        gui.rst.grid(column=4,columnspan=1)
        gui.rst.delete(0,END)
        gui.rst.insert(0,'5NN')
        
        gui.qth_lab.grid(columnspan=1,column=5,sticky=E+W)
        gui.qth.grid(column=5,columnspan=1)
        
        gui.boxes=[gui.call]
        gui.boxes.append(gui.rst)
        gui.boxes.append(gui.qth)
        
        if not gui.P.NO_HINTS:
            gui.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
            gui.hint.grid(column=6,columnspan=2)

            
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        call = gui.get_call().upper()
        rst  = gui.get_rst().upper()
        qth  = gui.get_qth().upper()
        valid = len(call)>=3 and len(rst)>0 and len(qth)>0

        MY_STATE = self.P.SETTINGS['MY_STATE']
        exch_out = '599,'+MY_STATE
        
        return exch,valid,exch_out
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        gui.qth.delete(0,END)
        gui.qth.insert(0,a[0])

    # Hint insertion
    def insert_hint(self,h):

        gui=self.P.gui

        gui.qth.delete(0, END)
        gui.qth.insert(0,h[0])


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
            
