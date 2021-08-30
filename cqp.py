############################################################################################
#
# cpq.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for CA QSO Party.
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

# Keyin class for CQP
class CQP_KEYING():

    def __init__(self,P):
        self.P=P

        if P.USE_MASTER:
            P.HISTORY = P.HIST_DIR+'master.csv'
        else:
            #self.HISTORY = HIST_DIR+'CQP-CH-N1MM-05Oct2018.txt'
            P.HISTORY = HIST_DIR+'QSOP_CA*.txt'

        self.contest_name  = 'CQP'

        self.macros()

    # Routient to set macros for this contest
    def macros(self):

        Key='Cal QP'
        self.Key=Key
        MACROS[Key] = OrderedDict()
        MACROS[Key][0]     = {'Label' : 'CQ'        , 'Text' : 'CQ CQP [MYCALL] '}
        MACROS[Key][0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
        MACROS[Key][1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [SERIAL] [MYCOUNTY] '}
        MACROS[Key][2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] R73 CQP [MYCALL] [LOG]'}
        MACROS[Key][3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[Key][3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[Key][4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
        MACROS[Key][4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[Key][5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [SERIAL] [MYCOUNTY] '}
        MACROS[Key][6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[Key][6+12]  = {'Label' : '? '        , 'Text' : '? '}
        MACROS[Key][7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        
        MACROS[Key][8]     = {'Label' : 'NR 2x'    , 'Text' : '[SERIAL] [SERIAL] '}
        MACROS[Key][9]     = {'Label' : 'My QTH 2x' , 'Text' : '[MYCOUNTY] [MYCOUNTY] '}
        MACROS[Key][10]    = {'Label' : 'NR?'      , 'Text' : 'NR? '}
        MACROS[Key][11]    = {'Label' : 'QTH? '    , 'Text' : 'QTH? '}
        CONTEST[Key]=True

    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        state=P.MASTER[call]['state']
        if state=='CA':
            county=P.MASTER[call]['county']
            return county
        else:
            return state

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        sec=HIST[call]['state']
        if sec=='CA':
            sec  = HIST[call]['county']
                
        if iopt==1:
            
            done = len(sec)>0
            return sec,done

        else:

            self.call = call
            self.sec = sec

            serial = cut_numbers( randint(0, 999) )
            self.serial = serial
            
            txt2  = ' '+serial+' '+sec
            return txt2
            
    # Routine to process qso element repeats
    def repeat(self,label,exch2):
            
        if 'CALL' in label:
            txt2=self.call+' '+self.call
        elif 'NR?' in label:
            txt2=self.serial+' '+self.serial
        elif 'QTH?' in label:
            txt2=self.sec+' '+self.sec
        else:
            txt2=exch2

        return txt2

    # Error checking
    def error_check(self):
        P=self.P

        call2   = P.gui.get_call().upper()
        serial2 = P.gui.get_serial().upper()
        sec2    = P.gui.get_qth().upper()
        match   = self.call==call2 and self.serial==serial2 and self.sec==sec2

        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            print('Call sent:',self.call,' - received:',call2)
            P.gui.txt.insert(END,'Call sent: '+self.call+' - received: '+call2+'\n')
            
            print('Name sent:',self.name,' - received:',name2)
            P.gui.txt.insert(END,'Serial sent: '+self.serial+' - received: '+serial2+'\n')

            print('QTH  sent:',self.qth,' - received:',qth2)
            P.gui.txt.insert(END,'QTH  sent: '+self.sec+ ' - received: '+sec2+'\n')
            
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
        

    # Specific contest exchange for CQP
    def enable_boxes(self,gui):

        gui.contest=True
        gui.ndigits=3
        gui.hide_all()

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
        gui.qth_lab.grid(columnspan=cspan,column=col,sticky=E+W)
        gui.qth.grid(column=col,columnspan=cspan)
        
        gui.boxes=[gui.call]
        gui.boxes.append(gui.serial)
        gui.boxes.append(gui.qth)
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
        sec = gui.get_qth().upper()
        exch   = serial+','+sec
        valid = len(call)>=3 and len(sec)>0 and len(serial)>0
        
        MY_COUNTY   = self.P.SETTINGS['MY_COUNTY']
        exch_out = str(gui.cntr)+','+MY_COUNTY
        
        return exch,valid,exch_out
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        gui.serial.delete(0,END)
        gui.serial.insert(0,a[0])
        if len(a)>=2:
            gui.qth.delete(0,END)
            gui.qth.insert(0,a[1])

    # Hint insertion
    def insert_hint(self,h):

        gui=self.P.gui

        gui.qth.delete(0, END)
        gui.qth.insert(0,h[1])


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
            
