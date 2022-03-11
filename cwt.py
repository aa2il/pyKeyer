############################################################################################
#
# cwt.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
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

from tkinter import END,E,W
from collections import OrderedDict
from random import random
from rig_io.ft_tables import SST_SECS
from default import DEFAULT_KEYING
from utilities import cut_numbers,reverse_cut_numbers

############################################################################################

VERBOSITY=0

############################################################################################

# Keying class for CWops mini tests  - inherits base class
class CWOPS_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'CW Ops Mini-Test','CWOPS_*.txt')

        P.CONTEST_ID='CWOPS-CWT'
        self.number_key='cwops'
        

    # Routine to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ CWT [MYCALL] '}
        #MACROS[0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] [MYNAME] [MYSTATE] '}
        MACROS[1+12]  = {'Label' : 'NIL'       , 'Text' : 'NIL '}
        if self.P.PRACTICE_MODE or True:
            MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] RTU CWT [MYCALL] [LOG]'}
        else:
            MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] HNY EE [LOG]'}
        MACROS[2+12]  = {'Label' : 'TU/QRZ'    , 'Text' : '[CALL_CHANGED] 73 [NAME] CWT [MYCALL] [LOG]'}
        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [MYNAME] [MYSTATE]'}
        MACROS[5+12]  = {'Label' : 'S&P 2x'    , 'Text' : '[MYNAME] [MYNAME] [MYSTATE] [MYSTATE]'}
        MACROS[6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[6+12]  = {'Label' : '? '        , 'Text' : '? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}

        MACROS[8]     = {'Label' : 'Name 2x'   , 'Text' : '[MYNAME] [MYNAME] '}
        MACROS[9]     = {'Label' : 'State 2x'  , 'Text' : '[MYSTATE] [MYSTATE] '}
        MACROS[10]    = {'Label' : 'NAME?  '   , 'Text' : 'NAME? '}
        MACROS[11]    = {'Label' : 'NR?'       , 'Text' : 'NR? '}

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
            # Most of the time require a cwops number but once in a while use only state
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
        
        gui.name_lab.grid(columnspan=1,column=4,sticky=E+W)
        gui.name.grid(column=4,columnspan=2)
        gui.exch_lab.grid(columnspan=1,column=6,sticky=E+W)
        gui.exch.grid(column=6,columnspan=2)
        
        gui.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
        gui.hint.grid(column=7,columnspan=3)
        if self.P.NO_HINTS:
            gui.hint_lab.grid_remove()
            gui.hint.grid_remove()
            
        gui.boxes=[gui.call]
        gui.boxes.append(gui.name)
        gui.boxes.append(gui.exch)
        gui.boxes.append(gui.hint)
        
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        call=gui.get_call().upper()
        name=gui.get_name().upper()
        qth = gui.get_exchange().upper()
        exch=name+','+qth
        valid = len(call)>=3 and len(name)>0 and len(qth)>0
        
        MY_NAME   = self.P.SETTINGS['MY_NAME']
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
            gui.exch.delete(0,END)
            gui.exch.insert(0,a[1])

    # Hint insertion
    def insert_hint(self,h):

        gui=self.P.gui

        gui.name.delete(0, END)
        gui.name.insert(0,h[0])
        gui.exch.delete(0, END)
        if len(h)>2 and len( h[2] )>0:
            gui.exch.insert(0,h[2])
        elif len(h)>=2:
            gui.exch.insert(0,h[1])


