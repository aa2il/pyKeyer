#! /usr/bin/python
############################################################################################
#
# practice.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Functions related code and contest practice
#
# To Do - does the standalone version of this still work and under python 3?
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
import time
import random
import glob 
  
if sys.version_info[0]==3:
    from tkinter import END
else:
    from Tkinter import END
from load_history import *
from sidetone import *
from nano_io import nano_write
from cw_keyer import cut_numbers

############################################################################################

# Code practice
class CODE_PRACTICE():
    def __init__(self,P):

        print('CODE_PRACTICE: Init ...')
        self.P = P

        # Load history file providing a bunch of calls to play with
        print('CODE_PRACTICE: History=',P.HISTORY)
        if '*' in P.HISTORY:
            files=[]
            for fname in glob.glob(P.HISTORY):
                files.append(fname)
            files.sort()
            print(files)
            print(files[-1])
            #sys.exit(0)
            P.HISTORY=files[-1]
            print('CODE_PRACTICE: History=',P.HISTORY)
  
        if len(P.HISTORY)>0:
            self.HIST = load_history(P.HISTORY)
        else:
            print('Need a history file for practice mode')
            P.SHUTDOWN=True
            sys.exit(0)

        # For the Cal QP, it is helpful to only practice with CA stations
        self.calls = list(self.HIST.keys())
        self.Ncalls = len(self.calls)
        if P.CA_ONLY:
            print('CA ONLY - B4:',self.Ncalls)
            for call in self.calls:
                if self.HIST[call]['state']!='CA':
                    del self.HIST[call]
            self.calls = list(self.HIST.keys())
            self.Ncalls = len(self.calls)
            print('CA ONLY - AFTER:',self.Ncalls)
            #sys.exit(0)


    # Main routine that orchestrates code practice
    def run(self):

        # Loop until exit event is set
        while not self.P.Stopper.isSet():
            
            if self.P.PRACTICE_MODE:
                # Send a practice message
                self.practice_qso()

            else:
                time.sleep(1)
                

            
    # Routine to execute a single practice qso
    def practice_qso(self):

        P     = self.P
        HIST  = self.HIST
        keyer = P.keyer
        lock  = P.lock1
        MY_CALL = P.SETTINGS['MY_CALL']
    
        # Pick a call at random
        print('\nPRACTICE_QSO: Waiting 0 - Picking call ...')
        done = False
        repeats=False
        while not done:
            i = random.randint(0, self.Ncalls-1)
            call = self.calls[i]
            if P.NAQP:
                name  = HIST[call]['name']
                qth   = HIST[call]['state']
                done = len(name)>0 and len(qth)>0
            elif P.CWops:
                name,num,done = P.KEYING.qso_info(HIST,call,1)
            elif P.SST:
                name,qth,done = P.KEYING.qso_info(HIST,call,1)
            elif P.CW_OPEN:
                name,done = P.KEYING.qso_info(HIST,call,1)
            elif P.CAL_QP:
                sec,done = P.KEYING.qso_info(HIST,call,1)
            elif P.ARRL_10m:
                state=HIST[call]['state']
                done = len(state)>0
                print(i,call,state,done)
            else:
                done=True
            #print('PRACTICE_QSO:',call,HIST[call],done)

        # Wait for op to hit CQ
        print('PRACTICE_QSO: Waiting 1a - hit CQ ...',call,'...',P.gui.macro_label,'...')
        self.wait_for_keyer()
        Done=False
        while not Done:
            Done= ('CQ'  in P.gui.macro_label) or ('QRZ'   in P.gui.macro_label) or \
                  ('QSY' in P.gui.macro_label) or (MY_CALL in P.gui.macro_label) or \
                  ('Log QSO' in P.gui.macro_label and P.SPRINT) or \
                  self.P.Stopper.isSet()
            #print('PRACTICE_QSO: ',P.gui.macro_label,Done)
            time.sleep(0.1)
            #if not Done and keyer.evt.isSet():
            #    keyer.evt.clear()

        # Wait for handshake with keyer
        #print('PRACTICE_QSO: Waiting 1b - Handshake with keyer ...')
        if self.P.Stopper.isSet():
            return
        #print('PRACTICE_QSO: Waiting 1c - ',keyer.evt.isSet() )
        keyer.evt.clear()
        P.gui.macro_label=''
        print('PRACTICE_QSO: Waiting 1d - Got handshake with keyer ...')

        # Send a call
        done = False
        while not done:

            # Timing is critical so we make sure we have control
            lock.acquire()
            if P.PRACTICE_MODE:
                txt1 = ' '+call
                if P.KEYING:
                    txt2 = P.KEYING.qso_info(HIST,call,2)
                    exch2 = txt2
                elif P.NAQP:
                    name  = HIST[call]['name']
                    qth   = HIST[call]['state']
                    txt2  = ' '+name+' '+qth
                    exch2 = txt2
                elif P.ARRL_FD:
                    cat   = HIST[call]['fdcat']             # Category
                    sec   = HIST[call]['fdsec']             # Section
                    txt2  = ' '+cat+' '+sec
                    exch2 = txt2
                elif P.ARRL_VHF:
                    gridsq = HIST[call]['grid']             # grid square
                    txt2   = ' '+gridsq
                    exch2  = txt2
                elif P.CW_SS:
                    serial = cut_numbers( random.randint(0, 999) )
                    i      = random.randint(0, len(P.PRECS)-1)
                    prec   = P.PRECS[i]
                    chk    = HIST[call]['check']
                    sec    = HIST[call]['sec']
                    txt2   = ' '+serial+' '+prec+' '+call+' '+chk+' '+sec
                    exch2  = txt2
                    exch   = serial+','+prec+','+call+','+chk+','+sec
                elif P.CAL_QP999:
                    serial = cut_numbers( random.randint(0, 999) )
                    sec    = HIST[call]['state']
                    if sec=='CA':
                        sec  = HIST[call]['county']
                    txt2  = ' '+serial+' '+sec
                    exch2 = txt2
                    exch  = serial+','+sec
                elif P.ARRL_10m:
                    qth   = HIST[call]['state']
                    txt2  = ' 5NN '+qth
                    exch2 = txt2
                    exch  = '5NN,'+qth
                    #print('BURP: call/qth=',call,qth)
                    #print('BURP:',HIST[call])
                elif P.WPX:
                    serial = cut_numbers( random.randint(0, 999) )
                    txt2  = ' 5NN '+serial
                    exch2 = txt2
                    exch  = '5NN,'+serial
                elif P.IARU:
                    qth   = HIST[call]['ituz']
                    txt2  = ' 5NN '+qth
                    exch2 = txt2
                    exch  = '5NN,'+qth
                elif P.CQ_WW:
                    qth   = HIST[call]['cqz']
                    txt2  = ' 5NN '+qth
                    exch2 = txt2
                    exch  = '5NN,'+qth
                elif P.SPRINT:
                    serial = cut_numbers( random.randint(0, 999) )
                    name   = HIST[call]['name']
                    sec    = HIST[call]['state']
                    if P.LAST_MSG==0:
                        txt2 = MY_CALL+' '+serial+' '+name+' '+sec+' '+call
                    else:
                        txt1 = 'NA '+call+' CQ'
                        txt2 = MY_CALL+' '+call+' '+serial+' '+name+' '+sec
                    exch2  = txt2
                    exch   = serial+','+name+' '+sec
                else:
                    txt2='?????'
                    print('CODE PRACTICE: Unknown Contest')
                                    
                print('CODE PRACTICE: Sending call=',txt1)
                if self.P.NANO_IO:
                    nano_write(self.P.ser,txt1)
                else:
                    P.osc.send_cw(txt1,keyer.WPM,True)

            lock.release()

            # Wait for op to answer
            print('CODE PRACTICE: Waiting 2a - Answer ... keyer.evt=',keyer.evt.isSet())
            self.wait_for_keyer()
            while ('Reply' not in P.gui.macro_label) and ('?' not in P.gui.macro_label) and \
                  (MY_CALL not in P.gui.macro_label) and not self.P.Stopper.isSet():
                time.sleep(0.1)
            done = ('Reply' in P.gui.macro_label) or (MY_CALL in P.gui.macro_label)
            if not done:
                repeats=repeats or ('?' in P.gui.macro_label)
            P.gui.macro_label=''
            if self.P.Stopper.isSet():
                return
            keyer.evt.clear()
            print('CODE PRACTICE: Waiting 2b - Got Answer ... done=',done)

        # Send exchange 
        done = False
        while not done:
            
            if self.P.Stopper.isSet():
                return

            # Check if call is correct
            call2 = P.gui.get_call().upper()
            if call2!=call:
                txt2 = call+' '+txt2
            
            # Timing is critical so we make sure we have control
            lock.acquire()
            if P.PRACTICE_MODE:
                print('CODE PRACTICE: Sending exch=',txt2)
                if self.P.NANO_IO:
                    nano_write(self.P.ser,txt2)
                else:
                    P.osc.send_cw(txt2,keyer.WPM,True)
            lock.release()

            # Wait for op to answer
            print('CODE PRACTICE: Waiting 3a - Answer...')
            self.wait_for_keyer()
            label = P.gui.macro_label.upper()
            while ('TU' not in label) and ('?' not in label) and \
                  ('LOG' not in label) and not self.P.Stopper.isSet(): ### and ('CQ' not in label):
                time.sleep(0.1)
                label = P.gui.macro_label.upper()
                if len(label)>0:
                    print('CODE_PRACTICE 3a: label=',label,'\tkeyer.evt=',keyer.evt.isSet())
            if self.P.Stopper.isSet():
                return
            done = ('TU' in label) or ('LOG' in label)

            print('CODE PRACTICE: Waiting 3b - Answered ... done=',done,'\tlabel=',label)
            if not done:
                repeats=repeats or ('?' in label)
                #print('Repeats=',repeats)
                
                # Determine next element
                if P.KEYING:
                    txt2 = P.KEYING.repeat(label,exch2)
                elif 'CALL' in label:
                    txt2=call+' '+call
                elif P.CW_SS:
                    if 'NR?' in label:
                        txt2=serial+' '+serial
                    elif 'PREC?' in label:
                        txt2=prec+' '+prec
                    elif 'CHECK?' in label:
                        txt2=chk+' '+chk
                    elif 'SEC?' in label:
                        txt2=sec+' '+sec
                    else:
                        txt2=exch2
                elif P.NAQP:
                    if 'NAME?' in label:
                        txt2=name+' '+name
                    elif 'QTH?' in label:
                        txt2=qth+' '+qth
                    elif 'NR?' in label:
                        txt2=qth+' '+qth
                    else:
                        txt2=exch2
                elif P.ARRL_FD:
                    if 'CALL?' in label:
                        txt2=call+' '+call
                    elif 'NR?' in label:
                        txt2=cat+' '+cat
                    elif 'QTH?' in label or  'SEC?' in label:
                        txt2=sec+' '+sec
                    else:
                        txt2=exch2
                elif P.ARRL_VHF:
                    if 'CALL?' in label:
                        txt2=call+' '+call
                    elif 'GRID?' in label or 'QTH?' in label or  'SEC?' in label:
                        txt2=gridqs+' '+gridsq
                    else:
                        txt2=exch2
                elif P.WPX:
                    if 'NR?' in label:
                        txt2=serial+' '+serial
                    else:
                        txt2=exch2
                elif P.IARU or P.CQ_WW or P.ARRL_10m:
                    if 'NR?' in label or 'QTH?' in label:
                        txt2=qth+' '+qth
                    else:
                        txt2=exch2
                elif P.SPRINT:
                    if 'NR?' in label:
                        txt2=serial+' '+serial
                    elif 'NAME?' in label:
                        txt2=name+' '+name
                    elif 'QTH?' in label:
                        txt2=sec+' '+sec
                    else:
                        txt2=exch2

                # Get ready to try again
                P.gui.macro_label=''
                keyer.evt.clear()
            
        # Error checking - keyer event hasn't been cleared yet so the gui boxes won't get erased too fast
        print('CODE PRACTICE: Error check ...')
        call2 = P.gui.get_call().upper()
        if P.KEYING:
            match = P.KEYING.error_check()
        elif P.NAQP:
            name2 = P.gui.get_name().upper()
            qth2  = P.gui.get_qth().upper()
        elif P.ARRL_FD:
            cat2  = P.gui.get_cat().upper()
            sec2  = P.gui.get_qth().upper()
        elif P.ARRL_VHF:
            grid2  = P.gui.get_exchange().upper()
        elif P.CW_SS:
            serial = P.gui.get_serial().upper()
            prec   = P.gui.get_prec().upper()
            chk    = P.gui.get_check().upper()
            sec    = P.gui.get_qth().upper()
            #print('hey 1:',exch2)
            exch2  = serial+','+prec+','+call2+','+chk+','+sec
            #print('hey 2:',exch2)
        elif P.WPX:
            serial = P.gui.get_serial().upper()
            rst    = P.gui.get_rst().upper()
            exch2  = rst+','+serial
        elif P.IARU or P.CQ_WW or P.ARRL_10m:
            rst    = P.gui.get_rst().upper()
            qth2  = P.gui.get_qth().upper()
            exch2  = rst+','+qth2
        elif P.SPRINT:
            serial = P.gui.get_serial().upper()
            name2  = P.gui.get_name().upper()
            sec    = P.gui.get_qth().upper()
            exch2  = serial+','+name2+' '+sec

        # We have everything we need, now the main program can clear the gui boxes
        keyer.evt.clear()

        # Check call & exchange matching
        if P.NAQP:
            match = call==call2 and name==name2 and qth==qth2
        elif P.ARRL_FD:
            match = call==call2 and cat==cat2 and sec==sec2
        elif P.ARRL_VHF:
            match = call==call2 and gridsq==grid2 
        elif P.CW_SS or P.SPRINT or P.WPX or P.IARU or P.CQ_WW or P.ARRL_10m:
            match = call==call2 and exch==exch2

        if not match and not P.KEYING:
            txt='********************** ERROR **********************'
            print(txt)
            print('Call sent:',call,' - received:',call2)
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.insert(END,'Call sent: '+call+' - received: '+call2+'\n')

            if P.NAQP:
                print('Name sent:',name,' - received:',name2)
                print('QTH  sent:',qth,' - received:',qth2)
                P.gui.txt.insert(END,'Name sent: '+name+' - received: '+name2+'\n')
                P.gui.txt.insert(END,'QTH  sent: '+qth+ ' - received: '+qth2+'\n')
            elif P.ARRL_FD:
                print('Cat sent:',cat,' - received:',cat2)
                print('Sec  sent:',sec,' - received:',sec2)
                P.gui.txt.insert(END,'Cat sent: '+cat+' - received: '+cat2+'\n')
                P.gui.txt.insert(END,'Sec  sent: '+sec+ ' - received: '+sec2+'\n')
            elif P.ARRL_VHF:
                print('Grid sent:',gridsq,' - received:',grid2)
                P.gui.txt.insert(END,'Grid sent: '+gridsq+' - received: '+grid2+'\n')
            elif P.CW_SS or P.SPRINT or P.WPX or P.IARU or P.CQ_WW or P.ARRL_10m:
                print('Exchange sent:    ',exch)
                print('Exchange received:',exch2)
                P.gui.txt.insert(END,'Exchange sent:     '+exch+'\n')
                P.gui.txt.insert(END,'Exchange received: '+exch2+'\n')

            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)

        if P.ADJUST_SPEED:
            if not match:
                #print("ERROR - WPM DOWN ...")
                P.gui.set_wpm(-1)
            else:
                if not repeats:
                    #print("NO ERROR - WPM UP ...")
                    P.gui.set_wpm(+1)
        print(' ')

            
    # Routine to wait for keyer to flush - bail out if stopper gets set
    def wait_for_keyer(self):
        while not self.P.keyer.evt.wait(timeout=1):
            if self.P.Stopper.isSet():
                break
        return
        

# If this file is called as main, convert history file into simple log format
# At some point, chnage this into a function
if __name__ == '__main__':

    date_off = '20180101'
    time_off = '000000'
    freq=0
    band='0m'
    mode='CW'
    fp = open("HIST.LOG","w")
    fp.write('QSO_DATE_OFF,TIME_OFF,CALL,FREQ,BAND,MODE,SRX_STRING\n')

    HISTORY = '../history/data/SS_Call_History_Aug2018.txt'

    HIST = load_history(HISTORY)
    calls = list(HIST.keys())
    for call in calls:
        h=HIST[call]

        exch=h['name'] + ',' + h['state']        # NAQP
        fp.write('%s,%s,%s,%s,%s,%s,"%s"\n' % (date_off,time_off,call,str(freq),band,mode,exch))
        fp.flush()

    fp.close()
    sys.exit(0)
    
        
