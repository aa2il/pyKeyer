############################################################################################
#
# fd.py - Rev 1.0
# Copyright (C) 2021-3 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for ARRL Field Day
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

# Keyin class for ARRL Field Day
class FD_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'ARRL-FD','FD_202*.txt')
        P.CONTEST_ID='ARRL-FIELD-DAY'

    # Routient to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ FD [MYCALL] '}
        MACROS[0+12]  = {'Label' : 'QRZ? '     , 'Text' : 'QRZ? '}
        #MACROS[0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [MYCAT] [MYSEC] '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [MYCAT] [MYCAT] [MYSEC] [MYSEC] '}
        MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] R73 FD [MYCALL] [LOG]'}
        MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] FB [NAME] 73EE [LOG]'}
        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'CALL?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [MYCAT] [MYSEC]'}
        MACROS[5+12]  = {'Label' : 'S&P 2x'    , 'Text' : '[MYCAT] [MYCAT] [MYSEC] [MYSEC]'}
        MACROS[6]     = {'Label' : '? '        , 'Text' : '? '}
        MACROS[6+12]  = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        MACROS[7+12]  = {'Label' : 'RR'        , 'Text' : 'RR '}
        
        MACROS[8]     = {'Label' : 'Cat 2x'    , 'Text' : '[-2][MYCAT] [MYCAT] [+2]'}
        MACROS[9]     = {'Label' : 'Sec 2x'    , 'Text' : '[-2][MYSEC] [MYSEC] [+2]'}
        MACROS[10]    = {'Label' : 'NR?  '     , 'Text' : 'NR? '}
        MACROS[11]    = {'Label' : 'QTH? '     , 'Text' : 'SEC? '}
        MACROS[11+12] = {'Label' : 'QRL? '     , 'Text' : 'QRL? '}

        return MACROS

    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        cat   = P.MASTER[call]['fdcat']
        sec   = P.MASTER[call]['fdsec']
        return cat+' '+sec

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        cat   = HIST[call]['fdcat']             # Category
        qth   = HIST[call]['fdsec']             # Section

        if iopt==1:
            
            done = len(cat)>0 and len(qth)>0
            return done

        else:

            self.call = call
            self.cat = cat
            self.qth = qth

            txt2  = ' '+cat+' '+qth
            return txt2
            
    # Routine to process qso element repeats
    # Override default routine since NR is category for this contest
    # Perhaps there is a better name? Category? Need to Check FD rules
    def repeat(self,label,exch2):
            
        if 'CALL' in label:
            txt2=self.call+' '+self.call
        elif 'NR?' in label:
            txt2=self.cat+' '+self.cat
        elif 'QTH?' in label or  'SEC?' in label:
            txt2=self.qth+' '+self.qth
        else:
            txt2=exch2

        return txt2
            
    # Error checking
    def error_check(self):
        P=self.P

        call2 = P.gui.get_call().upper()
        cat2 = P.gui.get_cat().upper()
        qth2  = P.gui.get_qth().upper()
        match = self.call==call2 and self.cat==cat2 and self.qth==qth2

        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            print('Call sent:',self.call,' - received:',call2)
            P.gui.txt.insert(END,'Call sent: '+self.call+' - received: '+call2+'\n')
            
            print('Catergory sent:',self.cat,' - received:',cat2)
            P.gui.txt.insert(END,'Category sent: '+self.cat+' - received: '+cat2+'\n')

            print('QTH  sent:',self.qth,' - received:',qth2)
            P.gui.txt.insert(END,'QTH  sent: '+self.qth+ ' - received: '+qth2+'\n')

            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
            

    # Highlight function keys that make sense in the current context
    def highlight(self,gui,arg):

        if arg==0:
            gui.btns1[1].configure(background='green',highlightbackground='green')
            gui.btns1[2].configure(background='green',highlightbackground='green')
            gui.call.focus_set()
        elif arg==1:
            gui.cat.focus_set()
        elif arg==4:
            gui.btns1[5].configure(background='red',highlightbackground= 'red')
            gui.btns1[7].configure(background='red',highlightbackground= 'red')
            gui.btns1[1].configure(background='pale green',highlightbackground=gui.default_color)
            gui.btns1[2].configure(background='pale green',highlightbackground=gui.default_color)
        elif arg==7:
            gui.btns1[1].configure(background='pale green',highlightbackground=gui.default_color)
            gui.btns1[5].configure(background='indian red',highlightbackground=gui.default_color)
            gui.btns1[7].configure(background='indian red',highlightbackground=gui.default_color)
        

    # Specific contest exchange for field day
    def enable_boxes(self,gui):

        gui.contest=True
        gui.hide_all()
        self.macros=[1,None,2]

        gui.cat_lab.grid(columnspan=1,column=4,sticky=E+W)
        gui.cat.grid(column=4,columnspan=2)
        gui.qth_lab.grid(columnspan=1,column=6,sticky=E+W)
        gui.qth.grid(column=6,columnspan=2)

        gui.boxes=[gui.call]
        gui.boxes.append(gui.cat)
        gui.boxes.append(gui.qth)

        if not self.P.NO_HINTS:
            gui.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
            gui.hint.grid(column=7,columnspan=3)
            
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui
        
        call=gui.get_call().upper()
        cat=gui.get_cat().upper()
        qth = gui.get_qth().upper()
        exch=cat+','+qth
        valid = len(call)>=3 and len(cat)>0 and len(qth)>0

        MY_CAT     = self.P.SETTINGS['MY_CAT']
        MY_STATE    = self.P.SETTINGS['MY_STATE']
        exch_out = MY_CAT+','+MY_STATE

        qso2={}
        
        return exch,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        gui.cat.delete(0,END)
        gui.cat.insert(0,a[0])
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
        
        gui.cat.delete(0, END)
        gui.cat.insert(0,h[0])
        gui.qth.delete(0, END)
        gui.qth.insert(0,h[1])

