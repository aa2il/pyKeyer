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

############################################################################################

# Code practice
class CODE_PRACTICE():
    def __init__(self,P):

        print('CODE_PRACTICE INIT: History2=',P.HISTORY2)
        self.P = P

        # Load history file providing a bunch of calls to play with
        if '*' in P.HISTORY2:
            files=[]
            for fname in glob.glob(P.HISTORY2):
                files.append(fname)
            files.sort()
            print('file=',files)
            if len(files)>0:
                P.HISTORY2=files[-1]
            print('CODE_PRACTICE: History2=',P.HISTORY2)
  
        if P.HISTORY2==P.HIST_DIR+'master.csv':
            self.HIST=self.P.MASTER
        elif P.HISTORY2==P.HISTORY:
            self.HIST = self.P.HIST
        elif len(P.HISTORY2)>0:
            self.HIST = load_history(P.HISTORY2)
        else:
            print('Need a history file for practice mode')
            P.SHUTDOWN=True
            sys.exit(0)

        # For the Cal QP, it is helpful to only practice with CA stations
        self.calls = list(self.HIST.keys())
        self.Ncalls = len(self.calls)
        print('There are',self.Ncalls,'call signs to play with.')
        if P.PRACTICE_MODE and self.Ncalls==0:
            print('CODE_PRACTICE INIT: Need some calls to play with!!!!!')
            print('History2=',P.HISTORY2)
            P.SHUTDOWN=True
            sys.exit(0)
        if P.CA_ONLY:
            print('CA ONLY - B4:',self.Ncalls)
            for call in self.calls:
                if self.HIST[call]['state']!='CA':
                    #print('Deleting call=',call,'\t',self.HIST[call])
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

        DEBUG=1

        P     = self.P
        HIST  = self.HIST
        keyer = P.keyer
        lock  = P.lock1
        MY_CALL = P.SETTINGS['MY_CALL']
    
        # Pick a call at random
        if DEBUG:
            print('\nPRACTICE_QSO: Waiting 0 - Picking call ... ',self.Ncalls-1)
        done = False
        repeats=False
        ntries=0
        while not done:
            ntries+=1
            i = random.randint(0, self.Ncalls-1)
            call = self.calls[i]
            done = P.KEYING.qso_info(HIST,call,1)
            
            print('PRACTICE_QSO: call=',call,'\tdone=',done,'\thist=',HIST[call])
            if ntries>100:
                print('Something is rotten in Denmark!')
                P.SHUTDOWN=True
                sys.exit(0)

        # Wait for op to hit CQ
        if DEBUG:
            print('PRACTICE_QSO: Waiting 1a - op CQ ... call=',call,'\t',P.OP_STATE)
        self.wait_for_keyer()
        Done=False
        while not Done:
            #Done= ('CQ'  in P.gui.macro_label) or ('QRZ'   in P.gui.macro_label) or \
            #      ('QSY' in P.gui.macro_label) or (MY_CALL in P.gui.macro_label) or \
            #      ('Log QSO' in P.gui.macro_label and P.SPRINT) or \
            #      self.P.Stopper.isSet()
            Done = (P.OP_STATE & 1) or self.P.Stopper.isSet()
            time.sleep(0.1)

        # Abort
        if DEBUG:
            print('PRACTICE_QSO: Waiting 1b - Got CQ ...')
        if P.Stopper.isSet():
            return
        P.OP_STATE ^= 1          # Clear CQ/QRZ
        
        # Wait for handshake with keyer
        if DEBUG:
            print('PRACTICE_QSO: Waiting 1c for keyer ... ',keyer.evt.isSet() )
        keyer.evt.clear()
        if DEBUG:
            print('PRACTICE_QSO: Waiting 1d - Got handshake with keyer ...')

        # Send a call
        done = False
        while not done:

            # Timing is critical so we make sure we have control
            lock.acquire()
            txt1 = ' '+call
            if P.KEYING:
                txt2 = P.KEYING.qso_info(HIST,call,2)
                exch2 = txt2
            else:
                txt2='?????'
                print('PRACTICE_QSO: Unknown Contest')
                                    
            if DEBUG:
                print('PRACTICE_QSO: Sending call=',txt1)
            if self.P.NANO_IO:
                nano_write(self.P.ser,txt1)
            else:
                P.osc.send_cw(txt1,keyer.WPM,1,True)

            lock.release()

            # Wait for op to answer
            if DEBUG:
                print('PRACTICE_QSO: Waiting 2a - op exchange ... op_state=',P.OP_STATE)
            self.wait_for_keyer()
            while not Done:
                #Done = ('Reply' in P.gui.macro_label) or ('?' in P.gui.macro_label) or \
                #    (MY_CALL in P.gui.macro_label) or self.P.Stopper.isSet():
                Done = (P.OP_STATE & (2+8)) or self.P.Stopper.isSet()
                time.sleep(0.1)

            # Abort
            if DEBUG:
                print('PRACTICE_QSO: Waiting 2b - Got answer - op_state=',P.OP_STATE)
            if self.P.Stopper.isSet():
                return
            
            # Check for repeats
            #done = ('Reply' in P.gui.macro_label) or (MY_CALL in P.gui.macro_label)
            done = P.OP_STATE & 2
            P.OP_STATE ^= 2          # Clear Reply
            if not done:
                repeats=repeats or (P.OP_STATE & 8)
                P.OP_STATE ^= 8          # Clear Repeat

            # Wait for handshake with keyer
            if DEBUG:
                print('PRACTICE_QSO: Waiting 2c - keyer',P.OP_STATE,done,repeats)
            keyer.evt.clear()
            if DEBUG:
                print('PRACTICE_QSO: Waiting 2d - keyer ... done=',done,repeats)

        # Send exchange 
        done = False
        while not done:
            
            # Abort
            if self.P.Stopper.isSet():
                return

            # Check if call is correct
            call2 = P.gui.get_call().upper()
            if call2==None or txt2==None:
                print('\n@@@@@@@@@@@@@@@@@ PRACTICE_QSO: Unexpected string(s):\ncall=',call,
                      '\ncall2=',call2,'\ntxt2=',txt2)
            if call2!=call:
                txt2 = call+' '+txt2
            
            # Timing is critical so we make sure we have control
            lock.acquire()
            if DEBUG:
                print('PRACTICE_QSO: Sending exch=',txt2)
            if self.P.NANO_IO:
                nano_write(self.P.ser,txt2)
            else:
                P.osc.send_cw(txt2,keyer.WPM,1,True)
            lock.release()

            # Wait for op to answer
            if DEBUG:
                print('PRACTICE_QSO: Waiting 3a - op to Answer ... op_state=',P.OP_STATE)
            self.wait_for_keyer()
            while not Done:
                #Done = ('TU' in label) or ('?' in label) or \
                #    ('LOG' in label) ort self.P.Stopper.isSet()
                Done = (P.OP_STATE & 4) or self.P.Stopper.isSet()
                time.sleep(0.1)

            # Abort
            if DEBUG:
                print('PRACTICE_QSO: Waiting 3b - Got Answer, keyer ... op_state=',P.OP_STATE)
            if self.P.Stopper.isSet():
                return
            #done = ('TU' in label) or ('LOG' in label)
            done = P.OP_STATE & 4
            P.OP_STATE ^= 4          # Clear TU

            if DEBUG:
                print('PRACTICE_QSO: Waiting 3c - Got keyer ... done=',done)
            if not done:
                repeats=repeats or (P.OP_STATE & 8)
                P.OP_STATE ^= 8          # Clear Repeat
                label=P.gui.macro_label.upper()
                if DEBUG:
                    print('Waiting 3d - Repeats=',repeats,'\tlabel=',label)
                
                # Determine next elementx
                if P.KEYING:
                    txt2 = P.KEYING.repeat(label,exch2)
                elif 'CALL' in label:
                    txt2=call+' '+call

                # Get ready to try again
                keyer.evt.clear()
                
        # Error checking - keyer event hasn't been cleared yet so the gui boxes won't get erased too fast
        if DEBUG:
            print('PRACTICE_QSO: Error check ...')
        call2 = P.gui.get_call().upper()
        if P.KEYING:
            match = P.KEYING.error_check()

        # We have everything we need, now the main program can clear the gui boxes
        keyer.evt.clear()

        # Check call & exchange matching
        if not match and not P.KEYING:
            txt='********************** ERROR **********************'
            print(txt)
            print('Call sent:',call,' - received:',call2)
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.insert(END,'Call sent: '+call+' - received: '+call2+'\n')

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
    
        
