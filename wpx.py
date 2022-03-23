############################################################################################
#
# wpx.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
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
        
    # Routient to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ TEST [MYCALL] '}
        MACROS[0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU 5NN [SERIAL] '}
        MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] R73 [MYCALL] TEST [LOG]'}
        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU 5NN [SERIAL]'}
        MACROS[5+12]  = {'Label' : 'S&P 2x'    , 'Text' : 'TU 5NN [SERIAL] [SERIAL]'}
        MACROS[6]     = {'Label' : '?'         , 'Text' : '? '}
        MACROS[6+12]  = {'Label' : 'AGN? '     , 'Text' : 'AGN? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}

        MACROS[8]     = {'Label' : 'Serial 2x' , 'Text' : '[-2][SERIAL] [SERIAL][+2]'}
        MACROS[9]     = {'Label' : 'NR?'       , 'Text' : 'NR? '}
        MACROS[10]    = {'Label' : '-'         , 'Text' : ' '}
        MACROS[11]    = {'Label' : '-'         , 'Text' : ' '}

        return MACROS
        
    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        return None

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

        call2 = P.gui.get_call().upper()
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
            
            print('Serial sent:',self.name,' - received:',name2)
            P.gui.txt.insert(END,'Serial sent: '+self.serial+' - received: '+serial2+'\n')

            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
            

    # Specific contest exchange for CQ WPX
    def enable_boxes(self,gui):

        gui.contest=True
        gui.ndigits=-3
        gui.hide_all()
        self.macros=[1,None,2]

        gui.rstin_lab.grid(columnspan=1,column=4,sticky=E+W)
        gui.rstin.grid(column=4,columnspan=1)
        gui.rstin.delete(0,END)
        gui.rstin.insert(0,'5NN')
        
        gui.serial_lab.grid(columnspan=1,column=5,sticky=E+W)
        gui.serial.grid(column=5,columnspan=1)
        gui.counter_lab.grid()
        gui.counter.grid()

        gui.boxes=[gui.call]
        gui.boxes.append(gui.rstin)
        gui.boxes.append(gui.serial)

        if not gui.P.NO_HINTS:
            gui.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
            gui.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
            gui.hint.grid(column=6,columnspan=2)
            
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui
        
        call = gui.get_call().upper()
        rst  = gui.get_rst_in().upper()
        serial = gui.get_serial().upper()
        exch='5NN,'+serial
        valid = len(call)>=3 and len(rst)>0 and len(serial)>0

        exch_out = '599,'+str(gui.cntr)

        qso2={}
        
        return exch,valid,exch_out,qso2
    
    def dupe(self,a):
        #gui=self.P.gui
        #gui.serial.delete(0,END)
        #gui.serial.insert(0,a[0])
        return

    # Hint insertion
    def insert_hint(self,h=None):
        
        gui=self.P.gui


