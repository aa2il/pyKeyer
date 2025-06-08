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

DEBUG=1

############################################################################################

# Code practice
class CODE_PRACTICE():
    def __init__(self,P):

        print('CODE_PRACTICE INIT: History2=',P.HISTORY2)
        self.P = P
        self.enable = False
        self.last_id=None
        self.last_len=0
        self.last_cntr = -1

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
        print('PRACTICE->RUN: Beginning ...',flush=True)

        if self.P.PRACTICE_MODE:

            # Check that we have the right history file
            if self.last_id!=self.P.CONTEST_ID:
                self.load_practice_history()

        # Loop until exit event is set
        while not self.P.Stopper.isSet():
            #print('PRACTICE->RUN ...',self.enable,self.P.OP_STATE,
            #      self.P.HISTORY2,self.P.CONTEST_ID)
            self.enable |= self.P.OP_STATE

            if not self.enable:
                #print('PRACTICE->RUN: Checking keyer...',flush=True)
                self.enable = self.check_nano_txt2(['CQ'])
                if self.enable:
                    print('PRACTICE->RUN: Woo Hoo - Found CQ! Practice session ENABLED ...',flush=True)
            
            if self.P.PRACTICE_MODE:
                if self.enable:

                    # Check that we have the right history file - op could have changed it
                    if self.last_id!=self.P.CONTEST_ID:
                        self.load_practice_history()

                    # Send a practice message
                    self.practice_qso()

                else:
                    
                    time.sleep(.1)

            else:
                
                time.sleep(1)

    # Routine to perform handshake with the keyer
    def keyer_handshake(self,stage,to,done,repeats):
        
        P     = self.P
        keyer = P.keyer
        
        if DEBUG:
            print('PRACTICE_QSO: Waiting '+stage+'c for keyer ... set=',keyer.evt.isSet(),
                  '\top_state=',P.OP_STATE,'\tdone=',done,'\trepeats=',repeats,flush=True)                  
        keyer.evt.wait(timeout=to) 
        keyer.evt.clear()
        if DEBUG:
            print('PRACTICE_QSO: Waiting '+stage+'d - Got handshake with keyer ...')

            
    # Routine to execute a single practice qso
    def practice_qso(self):

        P       = self.P
        HIST    = self.HIST
        keyer   = P.keyer
        lock    = P.lock1
        MY_CALL = P.SETTINGS['MY_CALL']
        MY_EXCH = P.KEYING.exch_out
        repeats = False
        done    = False
    
        # Pick a call at random
        if DEBUG:
            print('\nPRACTICE_QSO: Waiting 0 - Picking call ... ncalls=',self.Ncalls-1)
            print('\tMY CALL=',MY_CALL)
            print('\tMY EXCH=',MY_EXCH)
        call = self.grab_call()

        # Wait for op to hit CQ
        if DEBUG:
            print('\nPRACTICE_QSO: Waiting 1a - op CQ ... call=',call,'\tOP_STATE=',P.OP_STATE,MY_CALL,flush=True)
        Done=False
        to=5
        while not Done:
            if self.check_nano_txt2([MY_CALL]):
                P.OP_STATE |= 1
                P.nano_txt=''
                to=0.1
            Done = (P.OP_STATE & (1+64)) or P.Stopper.isSet() 
            time.sleep(0.1)
        P.OP_STATE &= ~(1+64)          # Clear CQ/QRZ/Log

        # Abort ?
        if DEBUG:
            print('PRACTICE_QSO: Waiting 1b - Got CQ ...',flush=True)
        if P.Stopper.isSet():
            return
        
        # Wait for handshake with keyer
        self.keyer_handshake('1',to,done,repeats)

        # Get info for qso partner
        txt1 = ' '+call
        if P.KEYING:
            txt2 = P.KEYING.qso_info(HIST,call,2)
            exch2 = txt2
        else:
            txt2='?????'
            print('PRACTICE_QSO: Unknown Contest')
        #print('PRACTICE_QSO: txt1=',txt1)
        #print('PRACTICE_QSO: txt2=',txt2)
                                    
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

        # Fix-up exchange
        EXCH_OUT=MY_EXCH.copy()
        for i in range(len(MY_EXCH)):
            if 'SERIAL' in EXCH_OUT[i]:
                while P.MY_CNTR == self.last_cntr:
                    print('\tWaiting for counter update ...',P.MY_CNTR,self.last_cntr)
                    time.sleep(0.1)
                self.last_cntr = P.MY_CNTR
                EXCH_OUT[i] = str( P.MY_CNTR )
                #EXCH_OUT[i] = P.gui.get_counter()
            
        # Send a call
        while not done:

            # Timing is critical so we make sure we have control
            lock.acquire()
            if DEBUG:
                print('PRACTICE_QSO: Sending call=',txt1,'\top_state=',P.OP_STATE)
            if P.USE_KEYER:
                P.keyer_device.nano_write(txt1)
            if P.SIDETONE:
                P.osc.send_cw(txt1,keyer.WPM,1,True)
            lock.release()

            # Wait for op to answer
            Done=False
            if DEBUG:
                print('\nPRACTICE_QSO: Waiting 2a - op exchange ...\top_state=',P.OP_STATE,
                      'my exch=',EXCH_OUT,flush=True)
            to=5
            while not Done:
                if self.check_nano_txt2(EXCH_OUT):
                    print('--- GOT EXCH ---')
                    P.OP_STATE |= 2
                    P.nano_txt=''
                    to=.1
                elif self.check_nano_txt2(['?']):
                    print('--- GOT ? ---')
                    P.OP_STATE |= 8
                    P.nano_txt=''
                    to=.1
                Done = (P.OP_STATE & (2+8+16)) or P.Stopper.isSet() 
                #print('op_state=',P.OP_STATE,Done,flush=True)
                time.sleep(0.1)

            # Check for Abort
            if DEBUG:
                print('PRACTICE_QSO: Waiting 2b - Got answer - \top_state=',P.OP_STATE,'\tDone=',Done,flush=True)
            if P.Stopper.isSet():
                return
            
            # Check for repeats
            done = P.OP_STATE & (2+32)
            P.OP_STATE &= ~(2+32)          # Clear Reply
            if not done:
                repeats=repeats or (P.OP_STATE & 8)
                P.OP_STATE &= ~8          # Clear Repeat

            # Wait for handshake with keyer
            self.keyer_handshake('2',to,done,repeats)

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
            if P.Stopper.isSet():
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
            if P.USE_KEYER:
                P.keyer_device.nano_write(txt2)
            if P.SIDETONE:
                P.osc.send_cw(txt2,keyer.WPM,1,True)
            lock.release()

            # Wait for op to answer
            Done=False
            if DEBUG:
                print('PRACTICE_QSO: Waiting 3a - op to Answer ... op_state=',P.OP_STATE,flush=True)
            while not Done:
                #logged = len(P.nano_txt)>0 and (P.OP_STATE & 64)
                #print('--- LOOGED= ---',logged)
                if self.check_nano_txt2(['73' ]) or \
                   self.check_nano_txt2(['GL']) or \
                   self.check_nano_txt2(['EE']):
                    print('--- GOT 73/GL/EE ---')
                    P.OP_STATE |= 4
                    P.nano_txt=''
                elif self.check_nano_txt2(['?']):
                    print('--- GOT ? ---')
                    P.OP_STATE |= 8
                    P.nano_txt=''
                Done = (P.OP_STATE & (4+8+32)) or P.Stopper.isSet() # or logged
                time.sleep(0.1)

            # Abort ?
            if DEBUG:
                print('PRACTICE_QSO: Waiting 3b - Got Answer - \top_state=',P.OP_STATE)
            if P.Stopper.isSet():
                return
            done = P.OP_STATE & (4+32)
            P.OP_STATE &= ~(4+32)          # Clear TU

            # Wait for handshake with keyer
            self.keyer_handshake('3',to,done,repeats)

            if not done:
                repeats=repeats or (P.OP_STATE & 8)
                P.OP_STATE &= ~8          # Clear Repeat
                label=P.gui.macro_label.upper()
                if DEBUG:
                    print('Waiting 3e - Repeats=',repeats,'\tlabel=',label)
                
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
                if P.USE_KEYER:
                    P.keyer_device.nano_write(txt3)
                if P.SIDETONE:
                    P.osc.send_cw(txt3,keyer.WPM,1,True)
                lock.release()

                # Wait for op to log contact
                Done=False
                if DEBUG:
                    print('PRACTICE_QSO: Waiting 4a - op to Log contact ... op_state=',P.OP_STATE)
                while not Done:
                    Done = (P.OP_STATE & 64) or P.Stopper.isSet()
                    time.sleep(0.1)

                
        # Error checking - keyer event hasn't been cleared yet so the gui boxes won't get erased too fast
        call2 = P.gui.get_call().upper()
        if P.KEYING:
            match = P.KEYING.error_check()
        if DEBUG:
            print('PRACTICE_QSO: Error check ... match=',match)

        # We have everything we need, now the main program can clear the gui boxes
        keyer.evt2.clear()
        if DEBUG:
            print('PRACTICE_QSO: Keyer EVT2 Cleared ...',flush=True)

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
        P.nano_txt=''
        
    # Routine to look for special messages from the keyer
    def check_nano_txt2(self,msg):
        #print('CHECK NANO_TXT2: msg=',msg)

        n=len(self.P.nano_txt)
        if n!=self.last_len:
            print('\tnano_txt2=',self.P.nano_txt,flush=True)
            self.last_len=n

        result=True
        for m in msg:
            result = result and (m in self.P.nano_txt)
            
        return result


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

    
############################################################################################

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
    
        
