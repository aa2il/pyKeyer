#! /usr/bin/python
############################################################################################
#
# practice.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Functions related code and contest practice
#
# To Do - does the standalone version of this still work under python 3?
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

############################################################################################

# Code practice
class CODE_PRACTICE():
    def __init__(self,P):

        print('CODE_PRACTICE INIT: History2=',P.HISTORY2)
        self.P = P
        self.enable = False
        self.last_id=None

    def load_practice_history(self):
        P=self.P
        print('CODE_PRACTICE - Load Practice History',P.HISTORY2)
        self.last_id=P.CONTEST_ID

        # Load history file providing a bunch of calls to play with
        if '*' in P.HISTORY2:
            files=[]
            for fname in glob.glob(P.HISTORY2):
                files.append(fname)
            files.sort()
            print('file=',files)
            if len(files)>0:
                P.HISTORY2=files[-1]
            elif len(files)==0:
                #P.HISTORY2=P.HIST_DIR+'master.csv'                
                P.HISTORY2=P.HISTORY
            print('CODE_PRACTICE: History2=',P.HISTORY2)
  
        if P.HISTORY2==P.HIST_DIR+'master.csv':
            self.HIST = self.P.MASTER
        elif P.HISTORY2==P.HISTORY:
            self.HIST = self.P.HIST
        elif len(P.HISTORY2)>0:
            self.HIST,fname9 = load_history(P.HISTORY2)
        else:
            print('Need a history file for practice mode')
            P.SHUTDOWN=True
            sys.exit(0)
        print('P.HISTORY2=',P.HISTORY2,'\tLen Hist=',len(self.HIST))

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


    # P.OP_STATE:
    #    0 - Nothing
    #    1 - CQ or QRZ
    #    2 or 32 - Reply
    #    4 - TU
    #    8 - '?' but not QRZ?
            

    # Main routine that orchestrates code practice
    def run(self):
        print('PRACTICE->RUN Beginning ...')

        # Loop until exit event is set
        while not self.P.Stopper.isSet():
            #print('PRACTICE->RUN ...',self.enable,self.P.OP_STATE,
            #      self.P.HISTORY2,self.P.CONTEST_ID)
            self.enable |= self.P.OP_STATE
            
            if self.P.PRACTICE_MODE and self.enable:

                # Check that we have the right history file - put this in cwt.py
                if self.last_id!=self.P.CONTEST_ID:
                    self.load_practice_history()

                # Send a practice message
                self.practice_qso()

            else:
                
                time.sleep(1)
                

            
    # Routine to execute a single practice qso
    def practice_qso(self):

        DEBUG=1

        P       = self.P
        HIST    = self.HIST
        keyer   = P.keyer
        lock    = P.lock1
        MY_CALL = P.SETTINGS['MY_CALL']
        repeats = False
    
        # Pick a call at random
        if DEBUG:
            print('\nPRACTICE_QSO: Waiting 0 - Picking call ... ncalls=',self.Ncalls-1)
        call = self.grab_call()
        
        # Wait for op to hit CQ
        if DEBUG:
            print('PRACTICE_QSO: Waiting 1a - op CQ ... call=',call,'\tOP_STATE=',P.OP_STATE)
        self.wait_for_keyer()
        Done=False
        while not Done:
            Done = (P.OP_STATE & (1+64)) or self.P.Stopper.isSet()
            time.sleep(0.1)
        P.OP_STATE &= ~(1+64)          # Clear CQ/QRZ

        # Abort ?
        if DEBUG:
            print('PRACTICE_QSO: Waiting 1b - Got CQ ...')
        if P.Stopper.isSet():
            return
        
        # Wait for handshake with keyer
        if DEBUG:
            print('PRACTICE_QSO: Waiting 1c for keyer ... ',keyer.evt.isSet() )
        keyer.evt.clear()
        if DEBUG:
            print('PRACTICE_QSO: Waiting 1d - Got handshake with keyer ...')

        # Get info for qso partner
        done = False
        txt1 = ' '+call
        if P.KEYING:
            txt2 = P.KEYING.qso_info(HIST,call,2)
            exch2 = txt2
        else:
            txt2='?????'
            print('PRACTICE_QSO: Unknown Contest')
        print('PRACTICE_QSO: txt1=',txt1)
        print('PRACTICE_QSO: txt2=',txt2)
                                    
        # Decision time for sprints
        if P.CONTEST_ID=='NCCC-SPRINT':
            print('\nPRACTICE_QSO: Sprint!!!\tCONTEST_ID=',P.CONTEST_ID,'\tLAST_MACRO=',P.LAST_MACRO,'\n') 
            time.sleep(1)
            if P.LAST_MACRO in [0,7]:
                txt3 = ' '+txt2
            elif P.LAST_MACRO==2:
                txt3 = P.KEYING.qso_info(HIST,call,3)
                txt1 = ' '+txt3
            else:
                print('I dont know what I am doing here!!!')
                sys.exit(0)
            print('PRACTICE_QSO: txt3=',txt3)

        # Send a call
        while not done:

            # Timing is critical so we make sure we have control
            lock.acquire()
            if DEBUG:
                print('PRACTICE_QSO: Sending call=',txt1,'\top_state=',P.OP_STATE)
            if self.P.USE_KEYER:
                self.P.keyer_device.nano_write(txt1)
            else:
                P.osc.send_cw(txt1,keyer.WPM,1,True)

            lock.release()

            # Wait for op to answer
            Done=False
            if DEBUG:
                print('PRACTICE_QSO: Waiting 2a - op exchange ...\top_state=',P.OP_STATE)
            self.wait_for_keyer()
            while not Done:
                Done = (P.OP_STATE & (2+8+16)) or self.P.Stopper.isSet()
                time.sleep(0.1)

            # Abort
            if DEBUG:
                print('PRACTICE_QSO: Waiting 2b - Got answer - \top_state=',P.OP_STATE,'\tDone=',Done)
            if self.P.Stopper.isSet():
                return
            
            # Check for repeats
            done = P.OP_STATE & (2+16)
            P.OP_STATE &= ~(2+16)          # Clear Reply
            if not done:
                repeats=repeats or (P.OP_STATE & 8)
                P.OP_STATE &= ~8          # Clear Repeat

            # Wait for handshake with keyer
            if DEBUG:
                print('PRACTICE_QSO: Waiting 2c - keyer',P.OP_STATE,done,'\trepeats=',repeats,'\top_state=',P.OP_STATE)
            keyer.evt.clear()
            if DEBUG:
                print('PRACTICE_QSO: Waiting 2d - keyer ... done=',done,'\trepeats=',repeats,'\top_state=',P.OP_STATE)

        # Decision time again for sprints
        if P.CONTEST_ID=='NCCC-SPRINT':
            print('\nPRACTICE_QSO: Sprint @@@\tCONTEST_ID=',P.CONTEST_ID,'\tLAST_MACRO=',P.LAST_MACRO,'\n') 
            print('PRACTICE_QSO: txt1=',txt1)
            print('PRACTICE_QSO: txt2=',txt2)
            print('PRACTICE_QSO: txt3=',txt3)
            if P.LAST_MACRO in [1]:
                txt2=txt3

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
            if self.P.USE_KEYER:
                self.P.keyer_device.nano_write(txt2)
            else:
                P.osc.send_cw(txt2,keyer.WPM,1,True)
            lock.release()

            # Wait for op to answer
            Done=False
            if DEBUG:
                print('PRACTICE_QSO: Waiting 3a - op to Answer ... op_state=',P.OP_STATE)
            self.wait_for_keyer()
            while not Done:
                Done = (P.OP_STATE & (4+8+32)) or self.P.Stopper.isSet()
                time.sleep(0.1)

            # Abort ?
            if DEBUG:
                print('PRACTICE_QSO: Waiting 3b - Got Answer, keyer ... op_state=',P.OP_STATE)
            if self.P.Stopper.isSet():
                return
            done = P.OP_STATE & (4+32)
            P.OP_STATE &= ~(4+32)          # Clear TU

            if DEBUG:
                print('PRACTICE_QSO: Waiting 3c - Got keyer ... done=',done)
            if not done:
                repeats=repeats or (P.OP_STATE & 8)
                P.OP_STATE &= ~8          # Clear Repeat
                label=P.gui.macro_label.upper()
                if DEBUG:
                    print('Waiting 3d - Repeats=',repeats,'\tlabel=',label)
                
                # Determine next element
                if P.KEYING:
                    txt2 = P.KEYING.repeat(label,exch2)
                elif 'CALL' in label:
                    txt2=call+' '+call

                # Get ready to try again
                keyer.evt.clear()
                
        # Decision time once again for sprints
        if P.CONTEST_ID=='NCCC-SPRINT':
            print('\nPRACTICE_QSO: Sprint %%%\tCONTEST_ID=',P.CONTEST_ID,'\tLAST_MACRO=',P.LAST_MACRO,'\n') 
            
            # Timing is critical so we make sure we have control
            if P.LAST_MACRO==5:
                txt3=' TU'
                lock.acquire()
                if DEBUG:
                    print('PRACTICE_QSO: Sending final TU ...')
                if self.P.USE_KEYER:
                    self.P.keyer_device.nano_write(txt3)
                else:
                    P.osc.send_cw(txt3,keyer.WPM,1,True)
                lock.release()

                # Wait for op to log contact
                Done=False
                if DEBUG:
                    print('PRACTICE_QSO: Waiting 4a - op to Log contact ... op_state=',P.OP_STATE)
                self.wait_for_keyer()
                while not Done:
                    Done = (P.OP_STATE & 64) or self.P.Stopper.isSet()
                    time.sleep(0.1)

                
        # Error checking - keyer event hasn't been cleared yet so the gui boxes won't get erased too fast
        call2 = P.gui.get_call().upper()
        if P.KEYING:
            match = P.KEYING.error_check()
        if DEBUG:
            print('PRACTICE_QSO: Error check ... match=',match)

        # We have everything we need, now the main program can clear the gui boxes
        keyer.evt.clear()
        if DEBUG:
            print('PRACTICE_QSO: Keyer EVT Cleared ...')

        # Check call & exchange matching
        if not match and not P.KEYING:
            txt='********************** ERROR **********************'
            print(txt)
            print('Call sent:',call,' - received:',call2)
            P.gui.txt.insert(END,'\n\n'+txt+'\n')
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
            #print('Blah')
            if self.P.Stopper.isSet():
                break
        return


    # Routine to grab a call at random
    def grab_call(self):
        P     = self.P
        HIST  = self.HIST
        
        done = False
        ntries=0
        while not done:
            ntries+=1
            i = random.randint(0, self.Ncalls-1)
            call = self.calls[i]
            done = P.KEYING.qso_info(HIST,call,1)
            
            #print('PRACTICE_QSO: call=',call,'\tdone=',done,'\thist=',HIST[call])
            if ntries>100:
                print('\n**** PRACTICE_QSO: Something is rotten in Denmark - Probably a bad history file!!! ****\n')
                P.SHUTDOWN=True
                sys.exit(0)

        print('PRACTICE_QSO: call=',call,'\tdone=',done,'\thist=',HIST[call])
        return call

    

# If this file is called as main, convert history file into simple log format
# At some point, change this into a function
if __name__ == '__main__':

    date_off = '20180101'
    time_off = '000000'
    freq=0
    band='0m'
    mode='CW'
    fp = open("HIST.LOG","w")
    fp.write('QSO_DATE_OFF,TIME_OFF,CALL,FREQ,BAND,MODE,SRX_STRING\n')

    #HISTORY = '../history/data/SS_Call_History_Aug2018.txt'

    HIST,fname9 = load_history(HISTORY)
    calls = list(HIST.keys())
    for call in calls:
        h=HIST[call]

        exch=h['name'] + ',' + h['state']        # NAQP
        fp.write('%s,%s,%s,%s,%s,%s,"%s"\n' % (date_off,time_off,call,str(freq),band,mode,exch))
        fp.flush()

    fp.close()
    sys.exit(0)
    
        
