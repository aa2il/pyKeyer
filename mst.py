############################################################################################
#
# mst.py - Rev 1.0
# Copyright (C) 2021-2 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for ICWC Medium Speed mini-tests
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

import os
from tkinter import END,E,W
from collections import OrderedDict
from random import randint, random
from utilities import cut_numbers
from default import DEFAULT_KEYING
from datetime import datetime

############################################################################################

VERBOSITY=0

############################################################################################

# Keying class for CW Open - inherits base class
class MST_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'MST')

        P.HISTORY2 = os.path.expanduser('~/Python/history/data/ICWC-MST*.txt')
        P.CONTEST_ID='ICWC-MST'
        self.contest_duration = 1
        P.MAX_AGE = self.contest_duration *60
        
    # Routient to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ MST [MYCALL] '}
        MACROS[0+12]  = {'Label' : 'QRZ? '     , 'Text' : 'QRZ? '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [MYNAME] [SERIAL] '}
        #MACROS[1+12]  = {'Label' : 'NIL'       , 'Text' : 'NIL '}

        # Check date for any special greetings
        now = datetime.utcnow()
        if now.month==12 and now.day>=11 and now.day<28:
            MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] MC [NAME] EE [LOG]'}
            MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] MC [NAME] 73EE [LOG]'}
            #MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'MC [MYNAME] [SERIAL] '}
        elif now.month==12 and now.day>=28:
            MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] MC HNY [NAME] EE [LOG]'}
            MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] MC HNY [NAME] EE [LOG]'}
            #MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'MC HNY [MYNAME] [SERIAL] '}
        elif now.month==1 and now.day<=14:
            MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] HNY [NAME] EE [LOG]'}
            MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] HNY [NAME] 73EE [LOG]'}
            #MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'HNY [MYNAME] [SERIAL] '}
        else:
            MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] [GDAY] [NAME] 73EE [LOG]'}
            MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] FB [NAME] 73EE [LOG]'}

        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [MYNAME] [SERIAL] '}
        MACROS[6]     = {'Label' : '? '        , 'Text' : '? '}
        MACROS[6+12]  = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        MACROS[7+12]  = {'Label' : '73'        , 'Text' : '73 GL ee'}
        
        MACROS[8]     = {'Label' : 'My Name 2x', 'Text' : '[-2][MYNAME] [MYNAME] [+2]'}
        MACROS[9]     = {'Label' : 'NR 2x'     , 'Text' : '[-2][SERIAL] [SERIAL] [+2]'}
        MACROS[10]    = {'Label' : 'NAME? '    , 'Text' : 'NAME? '}
        MACROS[11]    = {'Label' : 'NR?'       , 'Text' : 'NR? '}
        MACROS[11+12] = {'Label' : 'QRL? '     , 'Text' : 'QRL? '}

        return MACROS

    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        name=P.MASTER[call]['name']
        return name

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        name=HIST[call]['name']
                
        if iopt==1:
            
            done = len(name)>0
            return done

        else:

            self.call = call
            self.name = name

            # Half the time, send serial as cut numbers 
            serial = randint(0, 199)
            x = random()
            print('Serial in=',serial,x)
            if x<=0.5:
                serial = cut_numbers( serial, ALL=True )
                print('Serial out=',serial)
            self.serial = str(serial)
            
            txt2  = ' '+name+' '+self.serial
            return txt2

        
    # Error checking
    def error_check(self):
        P=self.P

        call2   = P.gui.get_call().upper()
        name2    = P.gui.get_name().upper()
        serial2 = P.gui.get_serial().upper()
        match   = self.call==call2 and self.serial==serial2 and self.name==name2

        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            txt2='Call sent:'+self.call+'\t- received:'+call2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            txt2='Name sent:'+self.name+'\t- received:'+name2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')

            txt2='Serial sent:'+self.serial+'\t- received:'+serial2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')

            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
            

    # Specific contest exchange for MST
    def enable_boxes(self,gui):

        gui.contest=True
        gui.ndigits=-3
        gui.hide_all()
        self.macros=[1,None,2]
        
        col=0
        cspan=3
        gui.call_lab.grid(column=col,columnspan=cspan)
        gui.call.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.name_lab.grid(columnspan=cspan,column=col,sticky=E+W)
        gui.name.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.serial_lab.grid(column=col,columnspan=cspan)
        gui.serial.grid(column=col,columnspan=cspan)

        col+=cspan
        cspan=2
        gui.hint_lab.grid(column=col,columnspan=cspan)
        gui.hint.grid(column=col,columnspan=cspan)
        if self.P.NO_HINTS:
            gui.hint_lab.grid_remove()
            gui.hint.grid_remove()
        else:
            col+=cspan
                    
        cspan=12-col
        gui.scp_lab.grid(column=col,columnspan=cspan)
        gui.scp.grid(column=col,columnspan=cspan)
        if not self.P.USE_SCP:
            gui.scp_lab.grid_remove()
            gui.scp.grid_remove()
            
        gui.boxes=[gui.call]
        gui.boxes.append(gui.name)
        gui.boxes.append(gui.serial)
        gui.boxes.append(gui.hint)
        gui.boxes.append(gui.scp)
        
        gui.counter_lab.grid()
        gui.counter.grid()
        
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        call   = gui.get_call().upper()
        name   = gui.get_name().upper()
        serial = gui.get_serial().upper()
        exch   = serial+','+name
        valid  = len(call)>=3 and len(name)>0 and len(serial)>0
        
        MY_NAME  = self.P.SETTINGS['MY_NAME']
        exch_out = str(gui.cntr)+','+MY_NAME

        qso2={}
        
        return exch,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui
        if len(a)>=1:
            gui.name.delete(0,END)
            gui.name.insert(0,a[0])

    # Hint insertion
    def insert_hint(self,h=None):

        gui=self.P.gui

        if h==None:
            h = gui.hint.get()
        if type(h) == str:
            h = h.split(' ')

        #print('MST INSERT_HINT: h=',h)
        gui.name.delete(0, END)
        gui.name.insert(0,h[0])


