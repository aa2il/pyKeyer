############################################################################################
#
# ss.py - Rev 1.0
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
from macros import MACROS,CONTEST
from cw_keyer import cut_numbers

############################################################################################

VERBOSITY=0

############################################################################################

# Keying class for ARRL CW Sweepstakes
class SS_KEYING():

    def __init__(self,P):
        self.P=P

        if P.USE_MASTER:
            P.HISTORY = P.HIST_DIR+'master.csv'
        else:
            P.HISTORY = HIST_DIR+'SS_Call_History_Aug2018.txt'

        self.contest_name  = 'ARRL-SS-CW'
        self.macros()

    # Routient to set macros for this contest
    def macros(self):

        Key='ARRL CW SS'
        self.Key=Key
        MACROS[Key] = OrderedDict()
        MACROS[Key][0]     = {'Label' : 'CQ'        , 'Text' : 'CQ SS [MYCALL] '}
        MACROS[Key][0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
        MACROS[Key][1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [SERIAL] [MYPREC] [MYCALL] [MYCHECK] [MYSEC] '}
        MACROS[Key][2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] 73 de [MYCALL] QRZ? [LOG]'}
        MACROS[Key][3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[Key][3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[Key][4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
        MACROS[Key][4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[Key][5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [SERIAL] [MYPREC] [MYCALL] [MYCHECK] [MYSEC] '}
        MACROS[Key][6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[Key][6+12]  = {'Label' : '? '        , 'Text' : '? '}
        MACROS[Key][7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        
        MACROS[Key][8]     = {'Label' : 'NR?'      , 'Text' : 'NR? '}
        MACROS[Key][8+12]  = {'Label' : 'Serial 2x', 'Text' : '[SERIAL] [SERIAL] '}
        MACROS[Key][9]     = {'Label' : 'Prec?'    , 'Text' : 'PREC? '}
        MACROS[Key][9+12]  = {'Label' : 'Prec 2x'  , 'Text' : '[MYPREC] [MYPREC] '}
        MACROS[Key][10]    = {'Label' : 'Check?'   , 'Text' : 'CHK? '}
        MACROS[Key][10+12] = {'Label' : 'Check 2x' , 'Text' : '[MYCHECK] [MYCHECK] '}
        MACROS[Key][11]    = {'Label' : 'Sec?    ' , 'Text' : 'SEC? '}
        MACROS[Key][11+12] = {'Label' : 'Sec 2x'   , 'Text' : '[MYSEC] [MYSEC] '}
        CONTEST[Key]=True
        

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
            return chk,sec,done

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
    def repeat(self,label,exch2):
            
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

        call2   = P.gui.get_call().upper()
        serial2 = P.gui.get_serial().upper()
        prec2   = P.gui.get_prec().upper()
        chk2    = P.gui.get_check().upper()
        match   = self.call==call2 and self.serial==serial2 and \
            self.prec==prec2 and self.chk==chk2

        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            print('Call sent:',self.call,' - received:',call2)
            P.gui.txt.insert(END,'Call sent: '+self.call+' - received: '+call2+'\n')
            
            print('Serial sent:',self.name,' - received:',name2)
            P.gui.txt.insert(END,'Serial sent: '+self.serial+' - received: '+serial2+'\n')

            print('Cat sent:',self.cat,' - received:',cat2)
            P.gui.txt.insert(END,'Cat sent: '+self.cat+ ' - received: '+cat2+'\n')
            
            print('Check sent:',self.chk,' - received:',chk2)
            P.gui.txt.insert(END,'Check sent: '+self.chk+ ' - received: '+chk2+'\n')
            
            print('Prec sent:',self.prec,' - received:',prec2)
            P.gui.txt.insert(END,'Prec sent: '+self.prec+ ' - received: '+prec2+'\n')
            
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
            gui.serial.focus_set()
        elif arg==4:
            gui.btns1[5].configure(background='red',highlightbackground= 'red')
            gui.btns1[7].configure(background='red',highlightbackground= 'red')
            gui.btns1[1].configure(background='pale green',highlightbackground=gui.default_color)
            gui.btns1[2].configure(background='pale green',highlightbackground=gui.default_color)
        elif arg==7:
            gui.btns1[1].configure(background='pale green',highlightbackground=gui.default_color)
            gui.btns1[5].configure(background='indian red',highlightbackground=gui.default_color)
            gui.btns1[7].configure(background='indian red',highlightbackground=gui.default_color)
        

    # Specific contest exchange for CW Open
    def enable_boxes(self,gui):

        gui.contest=True
        gui.ndigits=3
        gui.hide_all()

        gui.serial_lab.grid()
        gui.serial.grid()
        gui.prec_lab.grid()
        gui.prec.grid()
        gui.call2_lab.grid()
        gui.call2.grid()
        gui.check_lab.grid()
        gui.check.grid()
        gui.qth_lab.grid(columnspan=3,column=8,sticky=E+W)
        gui.qth.grid(column=8,columnspan=2)

        gui.boxes=[gui.call]
        gui.boxes.append(gui.serial)
        gui.boxes.append(gui.prec)
        gui.boxes.append(gui.call2)
        gui.boxes.append(gui.check)
        gui.boxes.append(gui.qth)
        gui.counter_lab.grid()
        gui.counter.grid()
        
        if not gui.P.NO_HINTS:
            gui.call_lab.grid(column=0,columnspan=2)
            gui.call.grid(column=0,columnspan=2)
            gui.serial_lab.grid(column=2)
            gui.serial.grid(column=2)
            gui.prec_lab.grid(column=3)
            gui.prec.grid(column=3)
            gui.call2_lab.grid(column=4)
            gui.call2.grid(column=4)
            gui.check_lab.grid(column=5)
            gui.check.grid(column=5)
            gui.qth_lab.grid(column=6,columnspan=1)
            gui.qth.grid(column=6,columnspan=1)
            
            gui.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
            gui.hint.grid(column=7,columnspan=3)
            
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        call   = gui.get_call().upper()
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
        return exch,valid,exch_out
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        #if match2:
        gui.serial.delete(0,END)
        gui.serial.insert(0,a[0])
        if len(a)>=2:
            gui.prec.delete(0,END)
            if not gui.P.PRACTICE_MODE:
                gui.prec.insert(0,a[1])
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
        

    # Move on to next entry box & optionally play a macros
    def next_event(self,key,event,n=None):

        gui=self.P.gui

        if n!=None:
            gui.Send_Macro(n) 

        # Copy call into other entry field for it
        if event.widget==gui.call:
            call = gui.get_call().upper()
            gui.call2.delete(0, END)
            gui.call2.insert(0,call)
            
        if event.widget==gui.txt:
            #print('txt->call')
            next_widget = gui.call
        else:
            idx=gui.boxes.index(event.widget)
            nn = len(gui.boxes)
            #if idx==nn and key in ['Return','KP_Enter']:
            #    idx2 = idx
            if key in ['Tab','Return','KP_Enter']:
                idx2 = (idx+1) % nn
            elif key=='ISO_Left_Tab':
                idx2 = (idx-1) % nn
            else:
                print('We should never get here!!',idx,key,nn)
                idx2=idx
            #print(idx,'->',idx2)
            next_widget = gui.boxes[idx2]

        next_widget.focus_set()
        return next_widget
            


