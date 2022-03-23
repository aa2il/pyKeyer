############################################################################################
#
# cqww.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for CQ World Wdie contest
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
from default import DEFAULT_KEYING

############################################################################################

VERBOSITY=0

############################################################################################

# Keyin class for CQ World Wide
class CQWW_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'CQWW')


    # Routient to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]    = {'Label' : 'CQ'       , 'Text' : 'CQ WW [MYCALL] '}
        MACROS[0+12] = {'Label' : 'QRS '     , 'Text' : 'QRS PSE QRS '}
        MACROS[1]    = {'Label' : 'Reply'    , 'Text' : '[CALL] TU 5NN [MYCQZ] '}
        MACROS[2]    = {'Label' : 'TU/QRZ?'  , 'Text' : '[CALL_CHANGED] R73 WW [MYCALL] [LOG]'}
        MACROS[3]    = {'Label' : 'Call?'    , 'Text' : '[CALL]? '}
        MACROS[3+12] = {'Label' : 'Call?'    , 'Text' : 'CALL? '}

        MACROS[4]    = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
        MACROS[4+12] = {'Label' : 'His Call' , 'Text' : '[CALL] '}
        MACROS[5]    = {'Label' : 'S&P Reply', 'Text' : 'TU 5NN [MYCQZ] '}
        MACROS[6]    = {'Label' : 'AGN?'     , 'Text' : 'AGN? '}
        MACROS[6+12] = {'Label' : '? '       , 'Text' : '? '}
        MACROS[7]    = {'Label' : 'Log QSO'  , 'Text' : '[LOG] '}
        
        MACROS[8]    = {'Label' : 'Zone 2x'  , 'Text' : '[MYCQZ] [MYCQZ '}
        MACROS[9]    = {'Label' : 'NR?'      , 'Text' : 'NR? '}
        MACROS[10]   = {'Label' : 'B4'       , 'Text' : '[CALL] B4'}
        MACROS[11]   = {'Label' : 'Nil'      , 'Text' : 'NIL'}

        return MACROS

    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        qth  = P.MASTER[call]['cqz']
        return qth

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        qth = HIST[call]['cqz']

        if iopt==1:
            
            done = len(qth)>0
            return done

        else:

            self.call = call
            self.rst = '5NN'
            self.qth = qth

            txt2  = ' 5NN '+qth
            return txt2
            
    # Error checking
    def error_check(self):
        P=self.P

        call2 = P.gui.get_call().upper()
        rst2  = P.gui.get_rst_in().upper()
        qth2  = P.gui.get_qth().upper()
        match = self.call==call2 and self.rst==rst2 and self.qth==qth2

        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            txt2='Call sent:'+self.call+'\t- received:'+call2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            txt2='RST sent:'+self.rst+'\t- received:'+rst2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            txt2='QTH sent:'+self.qth+'\t- received:'+qth2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')

            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
            


    # Specific contest exchange for CQ World Wide
    def enable_boxes(self,gui):

        gui.contest=True
        gui.ndigits=-3
        gui.hide_all()
        self.macros=[1,None,2]

        gui.rstin_lab.grid(columnspan=1,column=4,sticky=E+W)
        gui.rstin.grid(column=4,columnspan=1)
        gui.rstin.delete(0,END)
        gui.rstin.insert(0,'5NN')
        
        gui.qth_lab.grid(columnspan=1,column=5,sticky=E+W)
        gui.qth.grid(column=5,columnspan=1)

        gui.boxes=[gui.call]
        gui.boxes.append(gui.rstin)
        gui.boxes.append(gui.qth)

        if not gui.P.NO_HINTS:
            gui.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
            gui.hint.grid(column=6,columnspan=2)
            
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui
        
        call = gui.get_call().upper()
        rst  = gui.get_rst_in().upper()
        qth = gui.get_qth().upper()
        exch='5NN,'+qth
        valid = len(call)>=3 and len(rst)>0 and len(qth)>0

        MY_CQ_ZONE = self.P.SETTINGS['MY_CQ_ZONE']
        exch_out = '599,'+MY_CQ_ZONE

        qso2={}
        
        return exch,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        gui.qth.delete(0,END)
        if len(a)>=2:
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

