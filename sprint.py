############################################################################################
#
# sprint.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for Sprints
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
from utilities import cut_numbers

############################################################################################

VERBOSITY=0

"""
# Sprints:
If you call CQ, you should send your report as follows:

HIS CALLSIGN  -  YOUR CALLSIGN   -  NUMBER  -  NAME  -  STATE

Example:

K5ZD W4AN 357 Bill GA

If you find a station S&Ping, then at the completion of the QSO the frequency will be yours.  In this case, you will want to send your callsign last so people on frequency know you are the person to call.

Example:

K5ZD 357 Bill GA W4AN

This is simply done by programming different CW memories with different messages.

Also remember, you MUST send the callsign of the station you are working and your callsign with each QSO.  

For RTTY, do this:

K6LL: NA K6LL K6LL CQ
AA3B: AA3B AA3B
K6LL: AA3B K6LL 132 DAVE AZ
AA3B: K6LL 136 BUD PA AA3B
K6LL: TU
(K6LL must now QSY)
K0AD: K0AD K0AD
AA3B: K0AD AA3B 137 BUD PA
K0AD : AA3B 119 AL MN K0AD
AA3B: R
(AA3B must now QSY)
K0AD: NA K0AD K0AD CQ
N6RO: N6RO N6RO

"""

############################################################################################

# Keyin class for ARRL Field Day
class SPRINT_KEYING():

    def __init__(self,P):
        self.P=P

        if P.USE_MASTER:
            P.HISTORY = P.HIST_DIR+'master.csv'
        else:
            P.HISTORY = HIST_DIR+'NAQPCW.txt'
            
        self.contest_name  = 'NCCC-Sprint'
        self.macros()

    # Routient to set macros for this contest
    def macros(self):

        Key='Sprint'
        self.Key=Key
        MACROS[Key] = OrderedDict()
        MACROS[Key][0]     = {'Label' : 'CQ'        , 'Text' : 'CQ NA [MYCALL] '}
        MACROS[Key][1]     = {'Label' : 'Reply1'    , 'Text' : '[CALL] [MYCALL] [SERIAL] [MYNAME] [MYSTATE] '}
        MACROS[Key][1+12]  = {'Label' : 'QSY -1'    , 'Text' : '[QSY-1] '}
        MACROS[Key][2]     = {'Label' : 'TU/QSY'    , 'Text' : '[LOG] [CALL_CHANGED] TU '}
        MACROS[Key][2+12]  = {'Label' : 'QSY +1'    , 'Text' : '[QSY+1] '}
        
        MACROS[Key][4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
        MACROS[Key][3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[Key][3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[Key][5]     = {'Label' : 'S&P Reply' , 'Text' : '[CALL] [SERIAL] [MYNAME] [MYSTATE] [MYCALL]'}
        MACROS[Key][6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[Key][6+12]  = {'Label' : '? '        , 'Text' : '? '}
        MACROS[Key][7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        MACROS[Key][7+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
        
        MACROS[Key][8]     = {'Label' : 'Call?'    , 'Text' : 'CALL? '}
        MACROS[Key][8+12]  = {'Label' : '[MYCALL] 2x' , 'Text' : '[MYCALL] [MYCALL] '}
        MACROS[Key][9]     = {'Label' : 'NR?'      , 'Text' : 'NR? '}
        MACROS[Key][9+12]  = {'Label' : 'Serial 2x', 'Text' : '[SERIAL] [SERIAL] '}
        MACROS[Key][10]    = {'Label' : 'NAME?'    , 'Text' : 'NAME? '}
        MACROS[Key][10+12] = {'Label' : 'Name 2x'  , 'Text' : '[MYNAME] [MYNAME] '}
        MACROS[Key][11]    = {'Label' : 'QTH?'     , 'Text' : 'QTH? '}
        MACROS[Key][11+12] = {'Label' : 'State 2x' , 'Text' : '[MYSTATE] [MYSTATE] '}
        CONTEST[Key]=True

    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        name  = P.MASTER[call]['name']
        state = P.MASTER[call]['state']
        if VERBOSITY>0:
            print('SPRINT_KEYEING - Hint:',name+' '+state)
        return name+' '+state

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        name  = HIST[call]['name'].split(' ')
        name  = name[0]
        qth   = HIST[call]['state']

        if iopt==1:
            
            done = len(name)>0 and len(qth)>0
            return name,qth,done

        else:

            self.call = call
            self.name = name
            self.qth = qth

            serial = cut_numbers( randint(0, 999) )
            self.serial = serial
            if self.P.LAST_MSG==0:
                txt2 = MY_CALL+' '+serial+' '+name+' '+sec+' '+call
            else:
                txt1 = 'NA '+call+' CQ'
                txt2 = MY_CALL+' '+call+' '+serial+' '+name+' '+sec

            return txt2
            
    # Routine to process qso element repeats
    def repeat(self,label,exch2):
            
        if 'CALL' in label:
            txt2=self.call+' '+self.call
        elif 'NR?' in label:
            txt2=serial+' '+serial
        elif 'NAME?' in label:
            txt2=self.name+' '+self.name
        elif 'QTH?' in label:
            txt2=self.qth+' '+self.qth
        else:
            txt2=exch2

        return txt2

    # Error checking
    def error_check(self):
        P=self.P

        call2 = P.gui.get_call().upper()
        serial2 = P.gui.get_serial().upper()
        name2 = P.gui.get_name().upper()
        qth2  = P.gui.get_qth().upper()
        match = self.call==call2 and self.serial==serial2 and self.name==name2 and self.qth==qth2
        
        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            print('Call sent:',self.call,' - received:',call2)
            P.gui.txt.insert(END,'Call sent: '+self.call+' - received: '+call2+'\n')
            
            print('Serial sent:',self.name,' - received:',name2)
            P.gui.txt.insert(END,'Serial sent: '+self.serial+' - received: '+serial2+'\n')

            print('Name sent:',self.name,' - received:',name2)
            P.gui.txt.insert(END,'Name sent: '+self.name+' - received: '+name2+'\n')

            print('QTH  sent:',self.qth,' - received:',qth2)
            P.gui.txt.insert(END,'QTH  sent: '+self.qth+ ' - received: '+qth2+'\n')
            
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
            gui.cat.focus_set()
        elif arg==4:
            gui.btns1[5].configure(background='red',highlightbackground= 'red')
            gui.btns1[7].configure(background='red',highlightbackground= 'red')
            gui.btns1[1].configure(background='pale green',highlightbackground=gui.default_color)
            gui.btns1[2].configure(background='pale green',highlightbackground=gui.default_color)
        elif arg==7:
            gui.btns1[1].configure(background='pale green',highlightbackground=gui.default_color)
            gui.btns1[5].configure(background='indian red',highlightbackground=gui.default_color)
            gui.btns1[7].configure(background='indian red',highlightbackground=gui.default_color)
        

    # Specific contest exchange for SST
    def enable_boxes(self,gui):

        gui.contest=True
        gui.hide_all()
        gui.ndigits=1

        gui.serial_lab.grid()
        gui.serial.grid()
        gui.name_lab.grid(columnspan=1,column=5,sticky=E+W)
        gui.name.grid(column=5,columnspan=1)
        gui.qth_lab.grid(columnspan=1,column=6,sticky=E+W)
        gui.qth.grid(column=6,columnspan=1)
        
        gui.boxes=[gui.call]
        gui.boxes.append(gui.serial)
        gui.boxes.append(gui.qth)
        gui.counter_lab.grid()
        gui.counter.grid()
        
        if not gui.P.NO_HINTS:
            gui.hint_lab.grid(columnspan=3,column=7,sticky=E+W)
            gui.hint.grid(column=7,columnspan=3)

    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        call=gui.get_call().upper()
        serial = self.get_serial().upper()
        name=gui.get_name().upper()
        qth = gui.get_qth().upper()
        exch=serial+' '+name+','+qth
        valid = len(call)>=3 and len(serial)>0 and len(name)>0 and len(qth)>0

        MY_NAME     = self.P.SETTINGS['MY_NAME']
        MY_STATE    = self.P.SETTINGS['MY_STATE']
        exch_out = str(gui.cntr)+','+MY_NAME+','+MY_STATE
        
        return exch,valid,exch_out
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        gui.cat.delete(0,END)
        gui.cat.insert(0,a[0])
        if len(a)>=2:
            gui.qth.delete(0,END)
            gui.qth.insert(0,a[1])
            
    # Hint insertion
    def insert_hint(self,h):

        gui=self.P.gui

        gui.cat.delete(0, END)
        gui.cat.insert(0,h[0])
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
            
