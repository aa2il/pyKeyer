############################################################################################
#
# cwt.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Keying routines for CWops mini tests.
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
from utilities import cut_numbers,reverse_cut_numbers
from datetime import datetime
from scoring import CWT_SCORING

############################################################################################

VERBOSITY=0

############################################################################################

# Keying class for CWops mini tests  - inherits base class
class CWOPS_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'CW Ops Mini-Test',SCP_FNAME='Shareable CWops data.xlsx')

        print('CWT INIT ...')
        P.HISTORY2 = os.path.expanduser('~/Python/history/data/CWOPS_*.txt')
        P.CONTEST_ID='CWOPS-CWT'
        self.number_key='cwops'
        self.contest_duration = 1
        P.MAX_AGE = self.contest_duration *60

        # On-the-fly scoring
        P.SCORING    = CWT_SCORING(P)

        """
        This code fragment gets the proper history list from the master file
        Eventually, we might go to this model where we only import the master.csv
        and each keying objct extracts what it wants but I have to think this through.
        One advantage of using CWT call history files is that include ops who participate
        but are not members

        print('# calls loaded=',len(P.HISTORY2))
        if len(P.HISTORY2)==0:
            P.HIST=[];
            for x in P.MASTER:
                if len(x['cwops'])>0:
                    #print('x=',x,len(x['cwops']))
                    P.HIST.append(x)
            print('New HIST len=',len(P.HIST))
            #sys.exit(0)
        """

    # Routine to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ CWT [MYCALL] '}
        MACROS[0+12]  = {'Label' : 'QRZ? '     , 'Text' : 'QRZ? '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] [MYNAME] [MYCWOPS] '}
        MACROS[1+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] TNX AGN [NAME] [MYCALL] [LOG]'}

        # Check date for any special greetings
        now = datetime.utcnow()
        if now.month==12 and now.day>=11 and now.day<28:
            GREETING  = "MC"
            GREETING1 = "MC"
            GREETING2 = "MC"
        elif (now.month==12 and now.day>=28) or (now.month==1 and now.day<=14):
            GREETING  = "HNY"
            GREETING1 = "HNY"
            GREETING2 = "HNY"
        elif now.month==7 and now.day<=7:
            GREETING  = "GBA"
            GREETING1 = "[HOWDY]"
            GREETING2 = "[GDAY]"
        else:            
            GREETING  = "TU"
            GREETING1 = "[HOWDY]"
            GREETING2 ="[GDAY]"
        MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] '+GREETING+' [MYCALL] [LOG]'}
        MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] '+GREETING1+' [NAME] [MYCALL] [LOG]'}

        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [MYNAME] [MYCWOPS]'}
        MACROS[5+12]  = {'Label' : 'S&P Reply' , 'Text' : GREETING2+' [NAME] [MYNAME] [MYCWOPS]'}
        MACROS[6]     = {'Label' : '? '        , 'Text' : '? '}
        MACROS[6+12]  = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        MACROS[7+12]  = {'Label' : 'RR'        , 'Text' : 'RR '}

        MACROS[8]     = {'Label' : 'Name 2x'   , 'Text' : '[-2][MYNAME] [MYNAME] [+2]'}
        MACROS[9]     = {'Label' : 'No. 2x'    , 'Text' : '[-2][MYCWOPS] [+2]'}
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
            num   = P.MASTER[call]['cwops']
        except:
            name  = ' '
            state  = ' '
            num   = ' '
            
        if VERBOSITY>0:
            print('CWOPS_KEYEING - Hint:',name+' '+state+' '+num)
            
        return name+' '+state+' '+num

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        name  = HIST[call]['name'].split(' ')
        name  = name[0]
                
        if iopt==1:
            
            #name  = HIST[call]['name']
            num   = HIST[call]['cwops']
            
            # Select criteria for a accepting a call
            # Most of the time, require a cwops number but once in a while use only state
            # This seems to be most realistic of what in encountered in the tests.
            done = len(name)>0 and len(num)>0                  # Need no. but some have state in no. field
            x = random()
            done =done and ((num not in SST_SECS) or (x<0.1))
                
            return done

        else:

            self.call = call
            self.name = name

            num = HIST[call]['cwops']
            if len(num)==0:
                qth = HIST[call]['state']
                txt2  = ' '+name+' '+qth
                self.qth = qth
            else:
                # Half the time, send as cut numbers 
                x = random()
                if num.isdigit() and x<=0.5:
                    num = cut_numbers( int(num), ALL=True )
                txt2  = ' '+name+' '+num
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
    

    # Specific contest exchange for CWops
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
        MY_NUM    = self.P.SETTINGS['MY_CWOPS']
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

