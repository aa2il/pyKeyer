############################################################################################
#
# cwopen.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for CW Ops CW Open.
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
from macros import MACROS,CONTEST
from cw_keyer import cut_numbers

############################################################################################

VERBOSITY=0

############################################################################################

# Base keying class for simple qsos
class DEFAULT_KEYING():

    def __init__(self,P,contest_name='CW Default',HISTORY=None):
        self.P=P
        self.contest_name  = contest_name 
        self.aux_cb=None

        P.HISTORY = P.HIST_DIR+'master.csv'
        if P.USE_MASTER or HISTORY==None:
            P.HISTORY = P.HIST_DIR+'master.csv'
        elif HISTORY:
            P.HISTORY = P.HIST_DIR+HISTORY
        else:
            P.HISTORY = None
            

    # Routient to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]  = {'Label' : 'CQ'      , 'Text' : 'CQ CQ CQ DE [MYCALL] [MYCALL] K '}
        MACROS[1]  = {'Label' : '[MYCALL]' , 'Text' : '[MYCALL] '}
        MACROS[2]  = {'Label' : 'Reply'   , 'Text' : 'RTU [RST] [MYSTATE] '}
        MACROS[3]  = {'Label' : 'OP'      , 'Text' : 'OP [MYNAME] [MYNAME] '}
        MACROS[4]  = {'Label' : 'QTH'     , 'Text' : 'QTH [MYSTATE] [MYSTATE] '}
        MACROS[5]  = {'Label' : '73'      , 'Text' : '73 '}
        MACROS[6]  = {'Label' : 'BK'      , 'Text' : 'BK '}
        MACROS[7]  = {'Label' : 'Call?'   , 'Text' : '[CALL]? '}
        MACROS[8]  = {'Label' : 'LOG it'  , 'Text' : '[LOG]'}
        MACROS[9]  = {'Label' : 'RST  '   , 'Text' : '[RST]'}
        MACROS[10] = {'Label' : 'V    '   , 'Text' : 'V'}
        MACROS[11] = {'Label' : 'Test '   , 'Text' : 'VVV [+10]VVV[-10] VVV'}

        return MACROS
        
    # Routine to generate a hint for a given call
    def hint(self,call):
        return None

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        if iopt==1:
            
            return True

        else:

            return ''
            
    # Routine to process qso element repeats
    def repeat(self,label,exch2):
            
        if 'CALL' in label:
            txt2=self.call+' '+self.call
        elif 'NR?' in label:
            txt2=self.serial+' '+self.serial
        elif 'NAME?' in label:
            txt2=self.name+' '+self.name
        elif 'QTH?' in label or 'GRID?' in label:
            txt2=self.qth+' '+self.qth
        elif 'PREC?' in label:
            txt2=self.prec+' '+self.prec
        elif 'CHECK?' in label:
            txt2=self.chk+' '+self.chk
        elif 'SEC?' in label:
            txt2=self.sec+' '+self.sec
        else:
            txt2=exch2

        return txt2

    # Error checking
    def error_check(self):
        P=self.P

        call2   = P.gui.get_call().upper()
        serial2 = P.gui.get_serial().upper()
        name2   = P.gui.get_name().upper()
        match   = self.call==call2 and self.serial==serial2 and self.name==name2

        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            txt2='Call sent:'+self.call+'\t- received:'+call2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            txt2='Serial sent:'+self.serial+'\t- received:'+serial2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')

            txt2='Name sent:'+self.name+'\t- received:'+name2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')

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
            gui.serial.focus_set()
        elif arg==4:
            gui.btns1[5].configure(background='red',highlightbackground= 'red')
            gui.btns1[7].configure(background='red',highlightbackground= 'red')
            gui.btns1[1].configure(background='pale green',highlightbackground=gui.default_color)
            gui.btns1[2].configure(background='pale green',highlightbackground=gui.default_color)
        elif arg==7:
            gui.btns1[1].configure(background='pale green',highlightbackground=gui.default_color)
            gui.btns1[5].configure(background='indian red',highlightbackground=gui.default_color)
            gui.btns1[7].configure(background='indian red',highlightbackground=gui.default_color)
        

    # Specific contest exchange for default qsos
    def enable_boxes(self,gui):

        gui.contest=True
        gui.ndigits=3
        gui.hide_all()
        self.macros=[1,None,2]
        #self.box_names=['call','serial','name']

        col=0
        cspan=3
        gui.call_lab.grid(column=col,columnspan=cspan)
        gui.call.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.serial_lab.grid(column=col,columnspan=cspan)
        gui.serial.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.name_lab.grid(columnspan=cspan,column=col,sticky=E+W)
        gui.name.grid(column=col,columnspan=cspan)
        
        gui.boxes=[gui.call]
        gui.boxes.append(gui.serial)
        gui.boxes.append(gui.name)
        gui.counter_lab.grid()
        gui.counter.grid()
        
        if not gui.P.NO_HINTS:
            col+=cspan
            cspan=3
            gui.hint_lab.grid(columnspan=cspan,column=col,sticky=E+W)
            gui.hint.grid(column=col,columnspan=cspan,sticky=E+W)
            
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        call=gui.get_call().upper()
        serial = gui.get_serial().upper()
        name = gui.get_name().upper()
        exch   = serial+','+name
        valid = len(call)>=3 and len(name)>0 and len(serial)>0
        
        MY_NAME   = self.P.SETTINGS['MY_NAME']
        exch_out = str(gui.cntr)+','+MY_NAME
        
        return exch,valid,exch_out
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        #gui.serial.delete(0,END)
        #gui.serial.insert(0,a[0])
        if len(a)>=2:
            gui.name.delete(0,END)
            gui.name.insert(0,a[1])

    # Hint insertion
    def insert_hint(self,h):

        gui=self.P.gui

        gui.name.delete(0, END)
        gui.name.insert(0,h[0])


    # Move on to next entry box & optionally play a macros
    def next_event(self,key,event):

        gui=self.P.gui

        if event.widget==gui.txt:
            #print('txt->call')
            next_widget = gui.call
        else:
            # Get current widget index
            idx=gui.boxes.index(event.widget)
            nn = len(gui.boxes)

            # Determine adjacent (next) widget
            if key in ['Tab','Return','KP_Enter']:
                idx2 = (idx+1) % nn
            elif key=='ISO_Left_Tab':
                idx2 = (idx-1) % nn
            else:
                print('We should never get here!!',idx,key,nn)
                idx2=idx
            #print(idx,'->',idx2)
            next_widget = gui.boxes[idx2]

            # Send a macro if needed
            if key=='Return' or key=='KP_Enter':
                n=self.macros[idx]
                if n!=None:
                    gui.Send_Macro(n)

        # Do any extra stuff that might be special to this contest
        if self.aux_cb:
            self.aux_cb(key,event)
            
        next_widget.focus_set()
        return next_widget
            