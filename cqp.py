############################################################################################
#
# cpq.py - Rev 1.0
# Copyright (C) 2021-4 by Joseph B. Attili, aa2il AT arrl DOT net
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

import os
from tkinter import END,E,W
from collections import OrderedDict
from random import randint
from utilities import cut_numbers
from default import DEFAULT_KEYING
from dx import Station
import hint
from rig_io import CQP_MULTS
import numpy as np
from utilities import error_trap

############################################################################################

VERBOSITY=0

############################################################################################

# Keyin class for CQP
class CQP_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'CQP')

        P.HISTORY2 = os.path.expanduser('~/Python/history/data/QSOP_CA*.txt')
        P.CONTEST_ID='CA-QSO-PARTY'

        # On-the-fly scoring
        self.nqsos=0
        self.BANDS = ['MW','160m','80m','40m','20m','15m','10m']         # Need MW for practice mode
        self.sec_cnt = np.zeros(len(CQP_MULTS),dtype=np.int32)
        self.init_scoring()
                
    # Routient to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ CQP [MYCALL] '}
        #MACROS[0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
        MACROS[0+12]  = {'Label' : 'QRZ? '     , 'Text' : 'QRZ? '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [SERIAL] [MYCOUNTY] '}
        MACROS[1+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] TNX AGN [NAME] EE [LOG]'}
        MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] 73 [MYCALL] [LOG]'}
        MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] GL [NAME] EE [LOG]'}
        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [SERIAL] [MYCOUNTY] '}
        MACROS[5+12]  = {'Label' : 'S&P 2x'    , 'Text' : 'TU [SERIAL] [SERIAL] [MYCOUNTY] [MYCOUNTY] '}
        MACROS[6]     = {'Label' : '? '        , 'Text' : '? '}
        MACROS[6+12]  = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        MACROS[7+12]  = {'Label' : 'RR'        , 'Text' : 'RR '}
        
        MACROS[8]     = {'Label' : 'NR 2x'     , 'Text' : '[-2][SERIAL]  [SERIAL] [+2]'}
        MACROS[8+12]  = {'Label' : 'His #?'    , 'Text' : '[SERIAL_IN]? '}
        MACROS[9]     = {'Label' : 'My QTH 2x' , 'Text' : '[-2][MYCOUNTY]  [MYCOUNTY] [+2]'}
        MACROS[9+12]  = {'Label' : 'STATE?'    , 'Text' : 'STATE? '}
        MACROS[10]    = {'Label' : 'NR?'       , 'Text' : 'NR? '}
        MACROS[10+12] = {'Label' : 'COUNTY? '  , 'Text' : 'COUNTY? '}
        MACROS[11]    = {'Label' : 'QTH? '     , 'Text' : 'QTH? '}
        MACROS[11+12] = {'Label' : 'QRL? '     , 'Text' : 'QRL? '}

        return MACROS

    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        self.NAME = P.MASTER[call]['name']
        state     = P.MASTER[call]['state']
        self.NUM  = P.MASTER[call]['cwops']
        if state=='CA':
            county=P.MASTER[call]['county']
            return county
        else:
            return state

        
    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        qth=HIST[call]['state']
        if qth=='CA':
            qth  = HIST[call]['county']
                
        if iopt==1:
            
            done = len(qth)>0
            return done

        else:

            self.call = call
            self.qth = qth

            serial = cut_numbers( randint(0, 999) )
            self.serial = serial
            
            txt2  = ' '+serial+' '+qth
            return txt2
            
    # Error checking
    def error_check(self):
        P=self.P

        call2   = P.gui.get_call().upper()
        serial2 = P.gui.get_serial().upper()
        qth2    = P.gui.get_qth().upper()
        match   = self.call==call2 and self.serial==serial2 and self.qth==qth2

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

            txt2='QTH sent: '+self.qth+'\t-\treceived: '+qth2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
            

    # Specific contest exchange for CQP
    def enable_boxes(self,gui):

        gui.contest=True
        gui.ndigits=1
        gui.hide_all()
        self.macros=[1,None,2]

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
        gui.qth_lab.grid(columnspan=cspan,column=col,sticky=E+W)
        gui.qth.grid(column=col,columnspan=cspan)
        
        if False:
            # Debug name insertion
            col+=cspan
            cspan=2
            gui.name_lab.grid(column=col,columnspan=cspan,sticky=E+W)
            gui.name.grid(column=col,columnspan=cspan)
        
        col+=cspan
        cspan=12-col
        gui.scp_lab.grid(column=col,columnspan=cspan)
        gui.scp.grid(column=col,columnspan=cspan)
        if not self.P.USE_SCP:
            gui.scp_lab.grid_remove()
            gui.scp.grid_remove()
            
        gui.boxes=[gui.call]
        gui.boxes.append(gui.serial_box)
        gui.boxes.append(gui.qth)
        gui.boxes.append(gui.scp)

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
        qth = gui.get_qth().upper()
        exch   = serial+','+qth
        valid = len(call)>=3 and len(qth)>0 and len(serial)>0
        
        MY_COUNTY   = self.P.SETTINGS['MY_COUNTY']
        exch_out = str(gui.cntr)+','+MY_COUNTY

        qso2={}
        
        return exch,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

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

        gui.qth.delete(0, END)
        gui.qth.insert(0,h[0])

        if False:
            gui.name.delete(0, END)
            gui.name.insert(0,self.NAME)
        if True:
            gui.info.delete(0, END)
            gui.info.insert(0,self.NAME+' '+self.NUM)

        
    # Hints if we're in the qth window
    def qth_hints(self):
        gui  = self.P.gui
        call = gui.get_call().upper()
        qth  = gui.get_qth().upper()
        if len(call)>=3:
            self.dx_station = Station(call)
            #pprint(vars(self.dx_station))

            h = hint.commie_fornia(self.dx_station,qth)
            if h:
                print('hint=',h)
                gui.hint.delete(0, END)
                gui.hint.insert(0,h)


    # On-the-fly scoring
    def scoring(self,qso):
        print("\nSCORING: qso=",qso)
        self.nqsos+=1        
        call=qso['CALL']

        try:
            qth  = qso["QTH"].upper()
            idx1 = CQP_MULTS.index(qth)
        except:
            self.P.gui.status_bar.setText('Unrecognized/invalid QTH!')
            error_trap('CQP->SCORING - Unrecognized/invalid QTH!')
            return
        self.sec_cnt[idx1] = 1
        
        mults = np.sum(self.sec_cnt)
        score=self.nqsos * mults
        print("SCORING: score=",score,self.nqsos,mults)

        txt='{:3d} QSOs  x {:3d} Mults = {:6,d} \t\t\t Last Worked: {:s}' \
            .format(self.nqsos,mults,score,call)
        self.P.gui.status_bar.setText(txt)
    
                
