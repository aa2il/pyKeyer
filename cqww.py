############################################################################################
#
# cqww.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for CQ World Wdie contest
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

# Keyin class for IARU HF championship
class CQWW_KEYING():

    def __init__(self,P):
        self.P=P

        P.HISTORY = P.HIST_DIR+'master.csv'

        self.contest_name  = 'CQWW'
        
        self.macros()

    # Routient to set macros for this contest
    def macros(self):

        Key='CQ WW'
        self.Key=Key

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


    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        qth  = P.MASTER[call]['cqz']
        return qth
    
    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        qth = HIST[call]['cqz']
        
        if iopt==1:
            
            done = len(qth)>0
            return qth,done

        else:

            self.call = call
            self.rst = '5NN'
            self.qth = qth
            
            txt2  = ' 5NN '+qth
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
        

    # Specific contest exchange for CQ Worldwide
    def enable_boxes(self,gui):

        gui.contest=True
        gui.ndigits=-3
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
        exch='5NN,'+qth
        valid = len(call)>=3 and len(rst)>0 and len(qth)>0

        MY_CQ_ZONE = self.P.SETTINGS['MY_CQ_ZONE']
        exch_out = '599,'+MY_CQ_ZONE
        
        return exch,valid,exch_out
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        gui.qth.delete(0,END)
        if len(a)>=2:
            gui.qth.insert(0,a[1])

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
            print(idx,'->',idx2)
            next_widget = gui.boxes[idx2]

        next_widget.focus_set()
        return next_widget
            
