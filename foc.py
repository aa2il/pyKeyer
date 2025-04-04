############################################################################################
#
# foc.py - Rev 1.0
# Copyright (C) 2024-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Keying routines for FOC BW.
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

import sys
import os
from tkinter import END,E,W
from collections import OrderedDict
from random import random
from rig_io import SST_SECS
from default import DEFAULT_KEYING
from utilities import cut_numbers,reverse_cut_numbers
from datetime import datetime

############################################################################################

VERBOSITY=0

############################################################################################

# Keying class for FOC BW contest
class FOCBW_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'FOC BW')

        print('FOC BW INIT ...')
        P.HISTORY2 = os.path.expanduser('~/Python/history/data/foc.txt')
        P.CONTEST_ID='FOC-BW'
        self.number_key='foc'
        self.contest_duration = 24
        P.MAX_AGE = self.contest_duration *60

        # On-the-fly scoring - NEW!
        #self.nqsos=0
        #self.calls=set([])
        self.P.SCORING.init_otf_scoring()

    # Routine to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ BW [MYCALL] '}
        MACROS[0+12]  = {'Label' : 'QRZ? '     , 'Text' : 'QRZ? '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] [RST] [MYNAME] [MYFOC] '}
        MACROS[1+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] TNX AGN [NAME] EE [LOG]'}

        MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] TU [NAME] 73 [MYCALL] [LOG]'}
        MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] TU [NAME] EE [LOG]'}

        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [NAME]  [RST] [MYNAME] [MYFOC]'}
        MACROS[5+12]  = {'Label' : 'S&P Agn'   , 'Text' : 'TNX AGN [NAME]  [RST] [MYNAME] [MYFOC]'}
        MACROS[6]     = {'Label' : '? '        , 'Text' : '? '}
        MACROS[6+12]  = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        MACROS[7+12]  = {'Label' : 'RR'        , 'Text' : 'RR '}

        MACROS[8]     = {'Label' : 'Name 2x'   , 'Text' : '[-2][MYNAME] [MYNAME] [+2]'}
        MACROS[9]     = {'Label' : 'No. 2x'    , 'Text' : '[-2][MYFOC] [MYFOC] [+2]'}
        MACROS[10]    = {'Label' : 'NAME?  '   , 'Text' : 'NAME? '}
        MACROS[10+12] = {'Label' : 'TEST'      , 'Text' : 'TEST '}
        MACROS[11]    = {'Label' : 'NR?'       , 'Text' : 'NR? '}
        MACROS[11+12] = {'Label' : 'QRL?'      , 'Text' : 'QRL? '}

        return MACROS
        
    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P
        
        try:
            name  = P.MASTER[call]['name']
            state = P.MASTER[call]['state']
            num   = P.MASTER[call][self.number_key]
        except:
            name  = ' '
            state  = ' '
            num   = ' '
            
        if VERBOSITY>0:
            print('FOCBW_KEYEING - Hint:',name+' '+state+' '+num)
            
        return name+' '+state+' '+num

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        name  = HIST[call]['name'].split(' ')
        name  = name[0]
                
        if iopt==1:
            
            num   = HIST[call][self.number_key]
            done = len(name)>0 and len(num)>0                  # Need no. but some have state in no. field
            return done

        else:

            self.call = call
            self.name = name

            num = HIST[call][self.number_key]

            # Half the time, send as cut numbers 
            x = random()
            if num.isdigit() and x<=0.5:
                num = cut_numbers( int(num), ALL=True )
                
            txt2  = '5NN '+name+' '+num
            self.qth = num
            self.serial=self.qth            # Need this bx the way the repeat keys are labeled
            
            return txt2

    # Error checking
    def error_check(self):
        P=self.P

        call2   = P.gui.get_call().upper()
        name2    = P.gui.get_name().upper()
        qth2  = P.gui.get_exchange().upper()

        qth1  = reverse_cut_numbers(self.qth)
        qth3  = reverse_cut_numbers(qth2)
            
        match = self.call==call2 and self.name==name2 and (self.qth==qth2 or qth1==qth3)

        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            print('Call sent:',self.call,' - received:',call2)
            P.gui.txt.insert(END,'Call sent: '+self.call+' - received: '+call2+'\n')
            
            print('Name sent:',self.name,' - received:',name2)
            P.gui.txt.insert(END,'Name sent: '+self.name+' - received: '+name2+'\n')

            print('QTH  sent:',self.qth,' - received:',qth2)
            P.gui.txt.insert(END,'QTH  sent: '+self.qth+ ' - received: '+qth2+'\n')

            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
    

    # Specific contest exchange for FOC BW
    def enable_boxes(self,gui):

        gui.contest=True
        gui.hide_all()
        self.macros=[1,None,None,None,2]
        
        col=0
        cspan=3
        gui.call_lab.grid(column=col,columnspan=cspan)
        gui.call.grid(column=col,columnspan=cspan)

        col+=cspan
        cspan=1
        gui.rstout_lab.grid(column=col,columnspan=cspan)
        gui.rstout.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=1
        gui.rstin_lab.grid(column=col,columnspan=cspan)
        gui.rstin.grid(column=col,columnspan=cspan)

        col+=cspan
        cspan=2
        gui.name_lab.grid(columnspan=cspan,column=col)
        gui.name.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.exch_lab.grid(columnspan=cspan,column=col)
        gui.exch.grid(column=col,columnspan=cspan)

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
        gui.boxes.append(gui.rstout)
        gui.boxes.append(gui.rstin)
        gui.boxes.append(gui.name)
        gui.boxes.append(gui.exch)
        gui.boxes.append(gui.hint)
        gui.boxes.append(gui.scp)

    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        call=gui.get_call().upper()
        name=gui.get_name().upper()
        qth = gui.get_exchange().upper()
        exch=name+','+qth
        valid = len(call)>=3 and len(name)>0 and len(qth)>0
        
        MY_NAME   = self.P.SETTINGS['MY_NAME']
        MY_NUM    = self.P.SETTINGS['MY_FOC']
        exch_out = MY_NAME+','+MY_NUM

        qso2={}
        
        return exch,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        gui.name.delete(0,END)
        gui.name.insert(0,a[0])
        if len(a)>=2:
            gui.exch.delete(0,END)
            gui.exch.insert(0,a[1])

    # Hint insertion
    def insert_hint(self,h=None):

        gui=self.P.gui

        if h==None:
            h = gui.hint.get()
        if type(h) == str:
            h = h.split(' ')

        if len(h)>=1:
            gui.name.delete(0, END)
            gui.name.insert(0,h[0])
            gui.exch.delete(0, END)
            if len(h)>2 and len( h[2] )>0:
                gui.exch.insert(0,h[2])
            elif len(h)>=2:
                gui.exch.insert(0,h[1])

    # On-the-fly scoring
    def scoring(self,qso):
        print("FOC->SCORING: qso=",qso)
        self.nqsos+=1
        mults = 1
        self.score=self.nqsos * mults
        print("SCORING: score=",self.score)

        #print(qso)
        call = qso['CALL']
        txt='{:3d} QSOs  \t\t\t Last Worked: {:s}' \
            .format(self.nqsos,call)
        self.P.gui.status_bar.setText(txt)
        
