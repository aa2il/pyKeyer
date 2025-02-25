############################################################################################
#
# sst.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Keying routines for slow speed mini tests.
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
from random import random
from rig_io import SST_SECS
from default import DEFAULT_KEYING
from datetime import datetime
import numpy as np
from utilities import error_trap
from scoring import SST_SCORING

############################################################################################

VERBOSITY=0

############################################################################################

# Keying class for SST mini tests  - inherits base class
class SST_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'SST',SCP_FNAME='~/Python/history/data/K1USNSST-*.txt')

        P.HISTORY2 = os.path.expanduser('~/Python/history/data/K1USNSST*.txt')
        P.CONTEST_ID='K1USN-SST'
        self.contest_duration = 1
        P.MAX_AGE = self.contest_duration*60

        # On-the-fly scoring
        P.SCORING = SST_SCORING(P,'SST')
        
    # Routine to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ SST [MYCALL] '}
        MACROS[0+12]  = {'Label' : 'QRZ? '     , 'Text' : 'QRZ? '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [MYNAME] [MYSTATE] '}
        #MACROS[1+12]  = {'Label' : 'Reply'     , 'Text' : '[CALL] TNX AGN [MYNAME] [MYSTATE] '}
        MACROS[1+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] TNX AGN [NAME] EE [LOG]'}
        
        # Check date for any special greetings
        now = datetime.utcnow()
        if now.month==12 and now.day>=11 and now.day<28:
            GREETING="MC"
        elif (now.month==12 and now.day>=28) or (now.month==1 and now.day<=14):
            GREETING="HNY"
        elif now.month==7 and now.day<=7:
            GREETING="GBA"
        else:            
            GREETING="[GDAY]"
        MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] '+GREETING+' [NAME] 73EE [LOG]'}

        MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] [HOWDY] [NAME] ESE [LOG]'}
        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : GREETING+' [NAME] [MYNAME] [MYSTATE]'}
        MACROS[5+12]  = {'Label' : 'S&P Reply' , 'Text' : 'TU [MYNAME] [MYSTATE]'}
        MACROS[6]     = {'Label' : '? '        , 'Text' : '? '}
        MACROS[6+12]  = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        MACROS[7+12]  = {'Label' : 'RR'        , 'Text' : 'RR '}
        
        MACROS[8]     = {'Label' : 'My Name 2x', 'Text' : '[-2][MYNAME] [MYNAME] [+2]'}
        MACROS[9]     = {'Label' : 'State 2x'  , 'Text' : '[-2][MYSTATE] [MYSTATE] [+2]'}
        MACROS[10]    = {'Label' : 'NAME?  '   , 'Text' : 'NAME? '}
        MACROS[10+12] = {'Label' : 'TEST'      , 'Text' : 'TEST '}
        MACROS[11]    = {'Label' : 'QTH? '     , 'Text' : 'QTH? '}
        MACROS[11+12] = {'Label' : 'QRL? '     , 'Text' : 'QRL? '}

        return MACROS

    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        name  = P.MASTER[call]['name']
        state = P.MASTER[call]['state']
                    
        if VERBOSITY>0:
            print('SST_KEYEING - Hint:',name+' '+state)
        return name+' '+state

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        name  = HIST[call]['name'].split(' ')
        name  = name[0]
        qth   = HIST[call]['state']

        if iopt==1:

            print('SST->QSO INFO:',name,qth)
            done = len(name)>0 and len(qth)>0
            return done

        else:

            self.call = call
            self.name = name
            self.qth = qth

            txt2  = ' '+name+' '+qth
            return txt2
        
    # Error checking
    def error_check(self):
        P=self.P

        call2 = P.gui.get_call().upper()
        name2 = P.gui.get_name().upper()
        qth2  = P.gui.get_qth().upper()
        match = self.call==call2 and self.name==name2 and self.qth==qth2

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

            txt2='QTH sent:'+self.qth+'\t- received:'+qth2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')

            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
            

    # Specific contest exchange for SST
    def enable_boxes(self,gui):

        gui.contest=True
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
        cspan=1
        gui.qth_lab.grid(columnspan=cspan,column=col,sticky=E+W)
        gui.qth.grid(column=col,columnspan=cspan)

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
        gui.boxes.append(gui.qth)
        gui.boxes.append(gui.hint)
        gui.boxes.append(gui.scp)
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui
        
        call=gui.get_call().upper()
        name=gui.get_name().upper()
        qth = gui.get_qth().upper()
        exch=name+','+qth
        valid = len(call)>=3 and len(name)>0 and len(qth)>0

        MY_NAME     = self.P.SETTINGS['MY_NAME']
        MY_STATE    = self.P.SETTINGS['MY_STATE']
        exch_out = MY_NAME+','+MY_STATE

        qso2={}
        
        return exch,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        gui.name.delete(0,END)
        gui.name.insert(0,a[0])
        if len(a)>=2:
            gui.qth.delete(0,END)
            gui.qth.insert(0,a[1])

    # Hint insertion
    def insert_hint(self,h=None):

        gui=self.P.gui
        #print('SST INSERT_HINT: h=',h)

        if h==None:
            h = gui.hint.get()
        if type(h) == str:
            h = h.split(' ')
        print('SST INSERT_HINT: h2=',h)

        gui.name.delete(0, END)
        gui.qth.delete(0, END)
        if len(h)>=1:
            name=h[0]
            gui.name.insert(0,name)
            if len(h)>=2:
                gui.qth.insert(0,h[1])

        #self.set_info_box()
        
        
############################################################################################

# Keying class for Weekly RTTY  mini test  - inherits SST class since the exchange is the same
class WRT_KEYING(SST_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'WRT')

        P.HISTORY2 = os.path.expanduser('~/Python/history/data/NAQPRTTY.txt')
        P.CONTEST_ID='WRT'
        self.contest_duration = 1
        P.MAX_AGE = self.contest_duration *60

        # On-the-fly scoring - NEW!
        self.nqsos=0
        self.BANDS = ['MW','160m','80m','40m','20m','15m','10m']         # Need MW for practice mode
        self.sec_cnt = np.zeros((len(SST_SECS),len(self.BANDS)),dtype=np.int32)
        self.init_scoring()

    # Routine to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ WRT [MYCALL] [MYCALL] '}
        MACROS[0+12]  = {'Label' : 'QRZ? '     , 'Text' : 'QRZ? '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [MYNAME] [MYSTATE] [CALL] '}
        MACROS[1+12]  = {'Label' : 'Reply'     , 'Text' : '[CALL] [MYNAME] [MYNAME] [MYSTATE]  [MYSTATE] [CALL] '}
        #MACROS[1+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] TNX AGN [NAME] EE [LOG]'}
        
        # Check date for any special greetings
        now = datetime.utcnow()
        if now.month==12 and now.day>=11 and now.day<28:
            GREETING="MC"
        elif (now.month==12 and now.day>=28) or (now.month==1 and now.day<=14):
            GREETING="HNY"
        elif now.month==7 and now.day<=7:
            GREETING="GBA"
        else:            
            GREETING="73"
        MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] '+GREETING+' [NAME] 73 [MY_CALL] [LOG]'}
        MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] [NAME] 73 [MY_CALL] QRZ? [LOG]'}
        
        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'  , 'Text' : ' [MYCALL] '}
        MACROS[4+12]  = {'Label' : '[MYCALL] 2x'  , 'Text' : ' [MYCALL] [MYCALL] '}
        
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [MYNAME] [MYSTATE] '}
        MACROS[5+12]  = {'Label' : 'S&P Reply' , 'Text' : 'TU [MYNAME] [MYNAME] [MYSTATE] [MYSTATE] '}
        MACROS[6]     = {'Label' : '? '        , 'Text' : 'AGN? '}
        MACROS[6+12]  = {'Label' : 'AGN?'      , 'Text' : 'AGN? AGN? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        #MACROS[7+12]  = {'Label' : 'RR'        , 'Text' : 'RR '}
        
        MACROS[8]     = {'Label' : 'My Name 2x', 'Text' : '[MYNAME] [MYNAME] '}
        MACROS[9]     = {'Label' : 'State 2x'  , 'Text' : '[MYSTATE] [MYSTATE] '}
        MACROS[10]    = {'Label' : 'NAME?  '   , 'Text' : 'NAME? '}
        MACROS[10+12] = {'Label' : 'TEST'      , 'Text' : 'TEST '}
        MACROS[11]    = {'Label' : 'QTH? '     , 'Text' : 'QTH? '}
        MACROS[11+12] = {'Label' : 'QRL? '     , 'Text' : 'QRL? '}

        return MACROS

        
