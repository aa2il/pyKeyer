############################################################################################
#
# arrl_ss.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for ARRL CW Sweepstakes
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

# Keying class for ARRL CW Sweepstakes
class SS_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'ARRL-SS-CW','SS_Call_History_Aug2018.txt')

        self.aux_cb = self.copy_call

    # Routient to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ SS [MYCALL] '}
        MACROS[0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [SERIAL] [MYPREC] [MYCALL] [MYCHECK] [MYSEC] '}
        MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] 73 de [MYCALL] QRZ? [LOG]'}
        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}

        MACROS[4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [SERIAL] [MYPREC] [MYCALL] [MYCHECK] [MYSEC] '}
        MACROS[6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[6+12]  = {'Label' : '? '        , 'Text' : '? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        
        MACROS[8]     = {'Label' : 'NR?'      , 'Text' : 'NR? '}
        MACROS[8+12]  = {'Label' : 'Serial 2x', 'Text' : '[SERIAL] [SERIAL] '}
        MACROS[9]     = {'Label' : 'Prec?'    , 'Text' : 'PREC? '}
        MACROS[9+12]  = {'Label' : 'Prec 2x'  , 'Text' : '[MYPREC] [MYPREC] '}
        MACROS[10]    = {'Label' : 'Check?'   , 'Text' : 'CHK? '}
        MACROS[10+12] = {'Label' : 'Check 2x' , 'Text' : '[MYCHECK] [MYCHECK] '}
        MACROS[11]    = {'Label' : 'Sec?    ' , 'Text' : 'SEC? '}
        MACROS[11+12] = {'Label' : 'Sec 2x'   , 'Text' : '[MYSEC] [MYSEC] '}

        return MACROS

    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        sec=P.MASTER[call]['sec']
        if sec=='':
            sec=P.MASTER[call]['state']
        if sec=='KP4':
            sec='PR'
        chk=P.MASTER[call]['check']
        return chk+' '+sec

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        chk    = HIST[call]['check']
        sec    = HIST[call]['sec']

        if iopt==1:
            
            done = len(chk)>0 and len(sec)>0
            return done

        else:

            self.call = call
            self.chk  = chk
            self.sec  = sec

            serial = cut_numbers( randint(0, 999) )
            self.serial = serial

            i      = randint(0, len(self.P.PRECS)-1)
            self.prec = self.P.PRECS[i]
            
            txt2   = ' '+serial+' '+self.prec+' '+call+' '+chk+' '+sec
            return txt2
            
    # Routine to process qso element repeats
    def repeat_old(self,label,exch2):
            
        if 'CALL' in label:
            txt2=self.call+' '+self.call
        elif 'NR?' in label:
            txt2=self.serial+' '+self.serial
        elif 'PREC?' in label:
            txt2=self.prec+' '+self.prec
        elif 'CHECK?' in label:
            txt2=self.chk+' '+self.chk
        elif 'SEC?' in label:
            txt2=self.sec+' '+self.sec
        else:
            txt2=exch2

            return txt2
            
    # Error checking
    def error_check(self):
        P=self.P

        call2 = P.gui.get_call().upper()
        serial2 = P.gui.get_serial().upper()
        prec2   = P.gui.get_prec().upper()
        chk2    = P.gui.get_check().upper()
        match   = self.call==call2 and self.serial==serial2 and \
            self.prec==prec2 and self.chk==chk2

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

            txt2='Prec sent:'+self.prec+'\t- received:'+prec2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            txt2='Check sent:'+self.check+'\t- received:'+check2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            txt2='Prec sent:'+self.prec+'\t- received:'+prec2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
            

    # Specific contest exchange for CW Open
    def enable_boxes(self,gui):

        gui.contest=True
        gui.ndigits=3
        gui.hide_all()
        self.macros=[1,None,None,None,None,2]

        col=0
        cspan=3
        gui.call_lab.grid(column=col,columnspan=cspan)
        gui.call.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=1
        gui.serial_lab.grid(column=col,columnspan=cspan)
        gui.serial.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=1
        gui.prec_lab.grid(column=col,columnspan=cspan)
        gui.prec.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.call2_lab.grid(column=col,columnspan=cspan)
        gui.call2.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=1
        gui.check_lab.grid(column=col,columnspan=cspan)
        gui.check.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=1
        gui.qth_lab.grid(column=col,columnspan=cspan)
        gui.qth.grid(column=col,columnspan=cspan)

        gui.boxes=[gui.call]
        gui.boxes.append(gui.serial)
        gui.boxes.append(gui.prec)
        gui.boxes.append(gui.call2)
        gui.boxes.append(gui.check)
        gui.boxes.append(gui.qth)
        gui.counter_lab.grid()
        gui.counter.grid()

        if not gui.P.NO_HINTS:
            col+=cspan
            cspan=3
            gui.hint_lab.grid(column=col,columnspan=cspan,sticky=E+W)
            gui.hint.grid(column=col,columnspan=cspan)
            
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui
        
        call = gui.get_call().upper()
        serial = gui.get_serial().upper()
        prec   = gui.get_prec().upper()
        call2  = gui.get_call2().upper()
        chk    = gui.get_check().upper()
        sec    = gui.get_qth().upper()
        exch   = serial+','+prec+','+call+','+chk+','+sec
        valid  = len(call)>0 and len(serial)>0 and len(prec)>0 and len(call)>0 and len(chk)>0 and len(sec)>0
        
        MY_CALL     = self.P.SETTINGS['MY_CALL']
        MY_SEC      = self.P.SETTINGS['MY_SEC']
        MY_CAT      = self.P.SETTINGS['MY_CAT']
        MY_PREC     = self.P.SETTINGS['MY_PREC']
        MY_CHECK    = self.P.SETTINGS['MY_CHECK']
        exch_out = str(gui.cntr)+','+MY_PREC+','+MY_CALL+','+MY_CHECK+','+MY_SEC

        qso2={}
        
        return exch,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        #if match2:
        #gui.serial.delete(0,END)
        #gui.serial.insert(0,a[0])
        
        if len(a)>=2:
            gui.prec.delete(0,END)
            if not gui.P.PRACTICE_MODE:
                #gui.prec.insert(0,a[1])
                if len(a)>=3:
                    gui.call2.delete(0,END)
                    gui.call2.insert(0,a[2])
                    if len(a)>=4:
                        gui.check.delete(0,END)
                        gui.check.insert(0,a[3])
                        if len(a)>=5:
                            gui.qth.delete(0,END)
                            gui.qth.insert(0,a[4])


    # Hint insertion
    def insert_hint(self,h):

        gui=self.P.gui
        gui.check.delete(0, END)
        gui.check.insert(0,h[0])
        gui.qth.delete(0, END)
        gui.qth.insert(0,h[1])

    # Copy call into call2 box
    def copy_call(self,key,event):
        
        gui=self.P.gui
        if event.widget==gui.call:
            call = gui.get_call().upper()
            gui.call2.delete(0, END)
            gui.call2.insert(0,call)
            
