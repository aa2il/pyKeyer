############################################################################################
#
# wpx.py - Rev 1.0
# Copyright (C) 2021-4 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for CQ World Prefix contest
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
from utilities import cut_numbers
from default import DEFAULT_KEYING

############################################################################################

VERBOSITY=0

############################################################################################

# Keyin class for CQ WPX championship
class WPX_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'CQWW')

        P.CONTEST_ID='CQ-WPX-CW'
        self.contest_duration = 48
        
    # Routient to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ TEST [MYCALL] '}
        MACROS[0+12]  = {'Label' : 'QRZ? '     , 'Text' : 'QRZ? '}
        
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU 5NN [SERIAL] '}
        MACROS[1+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] TNX AGN [NAME] EE [LOG]'}
        MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] 73 [MYCALL] [LOG]'}
        MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] GL [NAME] EE [LOG]'}
        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU 5NN [SERIAL]'}
        #MACROS[5+12]  = {'Label' : 'S&P 2x'    , 'Text' : 'TU 5NN [SERIAL] [SERIAL]'}
        MACROS[5+12]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [NAME] 5NN [SERIAL]'}
        MACROS[6]     = {'Label' : '?'         , 'Text' : '? '}
        MACROS[6+12]  = {'Label' : 'AGN? '     , 'Text' : 'AGN? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        MACROS[7+12]  = {'Label' : 'RR'        , 'Text' : 'RR'}
        
        MACROS[8]     = {'Label' : 'Serial 1x' , 'Text' : '[-3][SERIAL] [+3]'}
        #MACROS[8+12]  = {'Label' : 'Serial 1x' , 'Text' : '[-3][CUT_SERIAL] [+3]'}
        MACROS[9]     = {'Label' : 'NR?'       , 'Text' : 'NR? '}
        MACROS[10]    = {'Label' : '-'         , 'Text' : ' '}
        MACROS[11]    = {'Label' : '-'         , 'Text' : ' '}
        MACROS[11+12] = {'Label' : 'QRL? '     , 'Text' : 'QRL? '}

        return MACROS

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        if iopt==1:
            
            return True

        else:

            self.call = call
            self.rst = '5NN'
            serial = cut_numbers( randint(0, 999) )
            self.serial = serial
            
            txt2  = ' 5NN '+serial
            return txt2

    # Routine to process qso element repeats
    def repeat(self,label,exch2):

        if 'CALL' in label:
            txt2=self.call+' '+self.call
        elif 'NR?' in label:
            txt2=self.serial+' '+self.serial
        else:
            txt2=exch2

            return txt2
        
    # Error checking
    def error_check(self):
        P=self.P

        call2   = P.gui.get_call().upper()
        rst2  = P.gui.get_rst_in().upper()
        serial2 = P.gui.get_serial().upper()
        match = self.call==call2 and self.rst==rst2 and self.serial==serial2

        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            print('Call sent:',self.call,' - received:',call2)
            P.gui.txt.insert(END,'Call sent: '+self.call+' - received: '+call2+'\n')
            
            print('RST sent:',self.rst,' - received:',rst2)
            P.gui.txt.insert(END,'RST sent: '+self.rst+' - received: '+rst2+'\n')

            print('Serial sent:',self.serial,' - received:',serial2)
            P.gui.txt.insert(END,'Serial sent: '+self.serial+' - received: '+serial2+'\n')

            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
            

    # Specific contest exchange for CQ WPX
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
        cspan=1
        gui.rstin_lab.grid(columnspan=cspan,column=col,sticky=E+W)
        gui.rstin.grid(column=col,columnspan=cspan)
        gui.rstin.delete(0,END)
        gui.rstin.insert(0,'5NN')
        
        col+=cspan
        cspan=2
        gui.serial_lab.grid(columnspan=cspan,column=col,sticky=E+W)
        gui.serial_box.grid(column=col,columnspan=cspan)
        
        col+=cspan
        cspan=12-col
        gui.scp_lab.grid(column=col,columnspan=cspan)
        gui.scp.grid(column=col,columnspan=cspan)
        if not self.P.USE_SCP:
            gui.scp_lab.grid_remove()
            gui.scp.grid_remove()
            
        gui.boxes=[gui.call]
        gui.boxes.append(gui.rstin)
        gui.boxes.append(gui.serial_box)
        gui.boxes.append(gui.scp)
            
        gui.counter_lab.grid()
        gui.counter.grid()
        gui.inc_btn.grid()
        gui.dec_btn.grid()

    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        call   = gui.get_call().upper()
        rst  = gui.get_rst_in().upper()
        serial = gui.get_serial().upper()
        exch='5NN,'+serial
        valid = len(call)>=3 and len(rst)>0 and len(serial)>0
        
        exch_out = '599,'+str(gui.cntr)

        qso2={}
        
        return exch,valid,exch_out,qso2
    
    def dupe(self,a):
        return

    # Hint insertion
    def insert_hint(self,h=None):

        gui=self.P.gui


