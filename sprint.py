############################################################################################
#
# sprint.py - Rev 1.0
# Copyright (C) 2021-4 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for Sprints
#
############################################################################################
"""
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
from utilities import cut_numbers
from random import randint, random
import numpy as np

############################################################################################

VERBOSITY=0

############################################################################################

# Keying class for NCCC sprints - inherits base class
class SPRINT_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'NS')

        print('SPRINT INIT ...')
        P.HISTORY2 = os.path.expanduser('~/Python/history/data/NAQPCW.txt')
        P.CONTEST_ID='NCCC-SPRINT'
        self.contest_duration = 1
        P.MAX_AGE = self.contest_duration *60
                
        # On-the-fly scoring - Same as SST
        self.nqsos=0
        self.BANDS = ['MW','160m','80m','40m','20m','15m','10m']         # Need MW for pratice mode
        self.sec_cnt = np.zeros((len(SST_SECS),len(self.BANDS)),dtype=np.int)
        self.init_scoring()
        
    # Routine to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'NS [MYCALL] '}
        MACROS[0+12]  = {'Label' : 'QRZ? '     , 'Text' : 'QRZ? '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] [MYCALL] [SERIAL] [MYNAME] [MYSTATE] '}
        MACROS[1+12]  = {'Label' : 'QSY -1'    , 'Text' : '[QSY-1] '}
        
        MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] EE [LOG]'}
        MACROS[2+12]  = {'Label' : 'QSY +1'    , 'Text' : '[QSY+1] '}

        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : '[CALL] [SERIAL] [MYNAME] [MYSTATE] [MYCALL]'}

        MACROS[6]     = {'Label' : '? '        , 'Text' : '? '}
        MACROS[6+12]  = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        MACROS[7+12]  = {'Label' : 'RR'        , 'Text' : 'RR '}
        
        MACROS[8]     = {'Label' : 'Call?'    , 'Text' : 'CALL? '}
        MACROS[8+12]  = {'Label' : '[MYCALL] 2x' , 'Text' : '[MYCALL] [MYCALL] '}
        MACROS[9]     = {'Label' : 'NR?'      , 'Text' : 'NR? '}
        MACROS[9+12]  = {'Label' : 'Serial 2x', 'Text' : '[SERIAL] [SERIAL] '}
        MACROS[10]    = {'Label' : 'NAME?'    , 'Text' : 'NAME? '}
        MACROS[10+12] = {'Label' : 'Name 2x'  , 'Text' : '[MYNAME] [MYNAME] '}
        MACROS[11]    = {'Label' : 'QTH?'     , 'Text' : 'QTH? '}
        MACROS[11+12] = {'Label' : 'State 2x' , 'Text' : '[MYSTATE] [MYSTATE] '}
        
        return MACROS

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

        MY_CALL = self.P.SETTINGS['MY_CALL']
        name    = HIST[call]['name'].split(' ')
        name    = name[0]
        qth     = HIST[call]['state']

        if iopt==1:

            done = len(name)>0 and len(qth)>0
            print('SPRINT_KEYING->QSO INFO:',call,name,qth,done)
            return done

        else:

            self.call = call
            self.name = name
            self.qth  = qth

            serial = cut_numbers( randint(0, 999) )
            print('SPRINT_KEYING->QSO INFO: LAST_MACRO=',self.P.LAST_MACRO)
            if iopt==3:
                # Last macro was TU or MY CALL (S&Ping) - Tune into a another QSO
                # There's no need to remeber the serial no.
                call1 = self.P.practice.grab_call()
                txt2  = call1+' '+serial+' '+name+' '+qth+' '+call
            elif self.P.LAST_MACRO in [0,1,7]:
                # Last macro was a CQ - he inherits the freq
                txt2 = MY_CALL+' '+serial+' '+name+' '+qth+' '+call
                self.serial = serial
            else:
                # Respond to my S&P - I'll be inheritting the freq
                txt2 = MY_CALL+' '+call+' '+serial+' '+name+' '+qth
                self.serial = serial

            return txt2
            
    # Error checking
    def error_check(self):
        P=self.P

        call2   = P.gui.get_call().upper()
        serial2 = P.gui.get_serial().upper()
        name2   = P.gui.get_name().upper()
        qth2    = P.gui.get_qth().upper()
        match   = self.call==call2 and self.serial==serial2 and self.name==name2 and self.qth==qth2

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
        gui.ndigits=-3
        gui.hide_all()
        self.macros=[1,None,None,2]

        col=0
        cspan=3
        gui.call_lab.grid(column=col,columnspan=cspan)
        gui.call.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.serial_lab.grid(column=col,columnspan=cspan)
        gui.serial_box.grid(column=col,columnspan=cspan)
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
        gui.boxes.append(gui.serial_box)
        gui.boxes.append(gui.name)
        gui.boxes.append(gui.qth)
        gui.boxes.append(gui.hint)
        gui.boxes.append(gui.scp)

        gui.counter_lab.grid()
        gui.counter.grid()
        gui.inc_btn.grid()
        gui.dec_btn.grid()
        
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui
        
        call   = gui.get_call().upper()
        serial = gui.get_serial().upper()
        name   = gui.get_name().upper()
        qth    = gui.get_qth().upper()
        exch   = serial+' '+name+','+qth
        valid  = len(call)>=3 and len(serial)>0 and len(name)>0 and len(qth)>0

        MY_NAME     = self.P.SETTINGS['MY_NAME']
        MY_STATE    = self.P.SETTINGS['MY_STATE']
        exch_out = str(gui.cntr)+','+MY_NAME+','+MY_STATE

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

        if h==None:
            h = gui.hint.get()
        if type(h) == str:
            h = h.split(' ')

        gui.name.delete(0, END)
        gui.qth.delete(0, END)
        if len(h)>=1:
            gui.name.insert(0,h[0])
            if len(h)>=2:
                gui.qth.insert(0,h[1])
        

    # On-the-fly scoring - same as SST
    def scoring(self,qso):
        print("\nSCORING: qso=",qso)
        self.nqsos+=1        
        call=qso['CALL']

        band = qso["BAND"]
        idx = self.BANDS.index(band)

        try:
            qth  = qso["QTH"].upper()
            idx1 = SST_SECS.index(qth)
        except:
            self.P.gui.status_bar.setText('Unrecognized/invalid section!')
            error_trap('SST->SCORING - Unrecognized/invalid section!')
            return
        self.sec_cnt[idx1,idx] = 1
        
        mults = np.sum( np.sum(self.sec_cnt,axis=0) )
        score=self.nqsos * mults
        print("SCORING: score=",score,self.nqsos,mults)

        txt='{:3d} QSOs  x {:3d} Mults = {:6,d} \t\t\t Last Worked: {:s}' \
            .format(self.nqsos,mults,score,call)
        self.P.gui.status_bar.setText(txt)
                
