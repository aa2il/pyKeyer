############################################################################################
#
# cwopen.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
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

import os
from tkinter import END,E,W
from collections import OrderedDict
from random import randint
from utilities import cut_numbers
from default import DEFAULT_KEYING

############################################################################################

VERBOSITY=0

############################################################################################

# Keying class for CW Open - inherits base class
class CWOPEN_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'CW Open','CWOPS_*.txt')

        P.HISTORY2 = os.path.expanduser('~/Python/history/data/CWOPS_*.txt')
        P.CONTEST_ID='CWOPS-CWOPEN'
        self.number_key='cwops'

        # On-the-fly scoring - NEW!
        self.nqsos=0
        self.calls=set([])
        self.init_scoring()

        
    # Routient to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ CWO [MYCALL] '}
        #MACROS[0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
        MACROS[0+12]  = {'Label' : 'QRZ? '     , 'Text' : 'QRZ? '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] [SERIAL] [MYNAME] '}
        #MACROS[1+12]  = {'Label' : 'NIL'       , 'Text' : 'NIL '}
        MACROS[1+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] TNX AGN [NAME] EE [LOG]'}

        MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] TU [MYCALL] [LOG]'}
        MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] GL [NAME] EE [LOG]'}
        
        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [SERIAL] [MYNAME] '}
        MACROS[5+12]  = {'Label' : 'S&P 2x'    , 'Text' : '[SERIAL] [SERIAL] [MYNAME] [MYNAME] '}
        MACROS[6]     = {'Label' : '? '        , 'Text' : '? '}
        MACROS[6+12]  = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        MACROS[7+12]  = {'Label' : 'RR'        , 'Text' : 'RR '}
        
        MACROS[8]     = {'Label' : 'NR 2x'     , 'Text' : '[-2][SERIAL] [SERIAL] [+2]'}
        MACROS[9]     = {'Label' : 'My Name 2x', 'Text' : '[-2][MYNAME] [MYNAME] [+2]'}
        MACROS[10]    = {'Label' : 'NR?'       , 'Text' : 'NR? '}
        MACROS[10+12] = {'Label' : 'His #?'    , 'Text' : '[SERIAL_IN]? '}
        MACROS[11]    = {'Label' : 'NAME? '    , 'Text' : 'NAME? '}
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

            serial = cut_numbers( randint(0, 999) )
            self.serial = serial
            
            txt2  = ' '+serial+' '+name
            return txt2

        
    # Error checking
    def error_check(self):
        P=self.P

        call2   = P.gui.get_call().upper()
        serial2 = P.gui.get_serial().upper()
        name2    = P.gui.get_name().upper()
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
            

    # Specific contest exchange for CW Open
    def enable_boxes(self,gui):

        gui.contest=True
        gui.ndigits=1
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
        gui.serial_box.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.name_lab.grid(columnspan=cspan,column=col,sticky=E+W)
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
        gui.boxes.append(gui.name)
        gui.boxes.append(gui.scp)
        
        gui.counter_lab.grid()
        gui.counter.grid()
        gui.inc_btn.grid()
        gui.dec_btn.grid()
        
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

        qso2={}
        
        return exch,valid,exch_out,qso2,serial
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        if len(a)>=2:
            gui.name.delete(0,END)
            gui.name.insert(0,a[1])

    # Hint insertion
    def insert_hint(self,h=None):

        gui=self.P.gui

        if h==None:
            h = gui.hint.get()
        if type(h) == str:
            h = h.split(' ')
        
        gui.name.delete(0, END)
        gui.name.insert(0,h[0])


    # On-the-fly scoring
    def scoring(self,qso):
        print("SCORING: qso=",qso)
        self.nqsos+=1
        call=qso['CALL']
        self.calls.add(call)
        mults = len(self.calls)
        score=self.nqsos * mults
        print("SCORING: score=",score)

        txt='{:3d} QSOs  x {:3d} Uniques = {:6,d} \t\t\t Last Worked: {:s}' \
            .format(self.nqsos,mults,score,call)
        self.P.gui.status_bar.setText(txt)
