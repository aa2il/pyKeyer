#! /usr/bin/python3 -u
################################################################################
#
# pyKeyer.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
#    Main program for CW Keyer and server.

# Notes:
# Can also use something like this in FLDIGI macros to send text to server:
#     echo v | nc -u -w 0 localhost 7388
# Also, see ENV macro, F3 under 4th set to how to access serial number

# TO DO:
#    - Add a way to correct log on the fly
#    - Check if FLLOG works with the keyer
#
################################################################################
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
################################################################################

import sys
import serial
import practice 
import rig_io.socket_io as socket_io
import argparse
import threading
if sys.version_info[0]==3:
    import queue
else:
    import Queue
from subprocess import call
from keyer_gui import *
from macros import *
from nano_io import *
from load_history import *
from pprint import pprint
import rig_io.hamlibserver as rigctl
from sidetone import *
#from audio_io import WaveRecorder
import time
import os
from settings import *
from tcp_server import *

from cwops import *
from cwopen import *
from sst import *
from cqp import *
from vhf import *
from satellites import *

################################################################################

# User params
FS = 48000              # Playback rate
F0 = 700
AMP=0.5
HIST_DIR=os.path.expanduser('~/Python/history/data/')
VERBOSITY=0

if False:
    from datetime import datetime
    print(datetime.now().hour)
    sys.exit()

################################################################################

# Structure to contain processing params
class PARAMS:
    def __init__(self):

        # Process command line args
        # Can add required=True to anything that is required
        arg_proc = argparse.ArgumentParser()
        arg_proc.add_argument('-ss', action='store_true',help='ARRL Sweepstakes')
        arg_proc.add_argument('-naqp', action='store_true',help='NAQP')
        arg_proc.add_argument('-sst', action='store_true',help='K1USN SST')
        arg_proc.add_argument('-CWops', action='store_true',help='CWops')
        arg_proc.add_argument('-cwopen', action='store_true',help='CWops CW Open')
        arg_proc.add_argument('-wpx', action='store_true',help='CQ WPX')
        arg_proc.add_argument('-arrl_dx', action='store_true',help='ARRL DX')
        arg_proc.add_argument('-arrl_10m', action='store_true',help='ARRL 10m')
        arg_proc.add_argument('-cqp', action='store_true',help='California QP')
        arg_proc.add_argument('-fd', action='store_true',help='ARRL Field Day')
        arg_proc.add_argument('-vhf', action='store_true',help='ARRL VHF')
        arg_proc.add_argument('-sat', action='store_true',help='Satellites')
        arg_proc.add_argument('-sprint', action='store_true',help='NCCC CW Sprint')
        arg_proc.add_argument('-cqww', action='store_true',help='CQ Worldwide')
        arg_proc.add_argument('-iaru', action='store_true',help='IARU HF Championship')
        arg_proc.add_argument('-test', action='store_true',help='Disable TX')
        arg_proc.add_argument('-practice', action='store_true',help='Practice mode')
        arg_proc.add_argument('-sidetone', action='store_true',help='Sidetone Osc')
        arg_proc.add_argument('-nohints', action='store_true',help='No hints')
        arg_proc.add_argument('-capture', action='store_true',help='Record Rig Audio')
        arg_proc.add_argument('-force', action='store_true',help='Force rig connection (debugging)')
        arg_proc.add_argument('-master', action='store_true',help='Use Master History File')
        arg_proc.add_argument('-ca_only', action='store_true',help='Only use California Stations')
        arg_proc.add_argument("-wpm", help="CW speed",type=int,default=20)
        arg_proc.add_argument('-adjust', action='store_true',help='Adjust speed based on correct copy')
        arg_proc.add_argument("-rig", help="Connection Type",
                              type=str,default=["ANY"],nargs='+',
                              choices=CONNECTIONS+['NONE']+RIGS)
        arg_proc.add_argument("-port", help="Connection Port",
                              type=int,default=0)
        arg_proc.add_argument('-nano', action='store_true',help="Use Nano IO Interface")
        arg_proc.add_argument("-mode", help="Rig Mode",
                      type=str,default=None,
                      choices=[None,'CW','SSB'])
        arg_proc.add_argument("-rotor", help="Rotor connection Type",
                      type=str,default="NONE",
                      choices=['HAMLIB','NONE'])
        arg_proc.add_argument("-port2", help="Rotor onnection Port",
                              type=int,default=0)
        arg_proc.add_argument('-server', action='store_true',help='Start hamlib server')
        arg_proc.add_argument('-udp', action='store_true',help='Start UDP server')
        arg_proc.add_argument('-use_log_hist', action='store_true',help='Use history from log')
        args = arg_proc.parse_args()

        self.NAQP          = args.naqp
        self.SST           = args.sst
        self.CWops         = args.CWops
        self.CW_OPEN       = args.cwopen
        self.WPX           = args.wpx
        self.CW_SS         = args.ss
        self.SPRINT        = args.sprint
        self.CAL_QP        = args.cqp
        self.CQ_WW         = args.cqww
        self.IARU          = args.iaru
        self.ARRL_DX       = args.arrl_dx
        self.ARRL_10m      = args.arrl_10m
        self.ARRL_FD       = args.fd
        self.ARRL_VHF      = args.vhf
        self.SATELLITES    = args.sat
        self.CAPTURE       = args.capture
        self.RIG_AUDIO_IDX = None
        self.FORCE         = args.force
        self.TEST_MODE     = args.test
        self.NANO_IO       = args.nano
        self.PRACTICE_MODE = args.practice
        self.ADJUST_SPEED  = args.adjust and args.practice
        self.NO_HINTS      = args.nohints
        self.USE_MASTER    = args.master
        self.CA_ONLY       = args.ca_only
        #self.DIRECT_CONNECT = args.direct
        self.WPM           = args.wpm
        self.INIT_MODE     = args.mode
        
        self.connection    = args.rig[0]
        if len(args.rig)>=2:
            self.rig       = args.rig[1]
        else:
            self.rig       = None
            
        self.PORT          = args.port
        self.HAMLIB_SERVER = args.server
        self.UDP_SERVER    = args.udp
        self.USE_LOG_HISTORY = args.use_log_hist
        self.SIDETONE      = args.sidetone or self.PORT==1

        self.CONTEST       = CONTEST
        self.MACROS        = MACROS
        self.MY_CNTR       = 1
        self.PRECS         = PRECS
        self.SHUTDOWN      = False
        self.DIRTY         = False

        self.KEYING=None
        self.HIST_DIR=HIST_DIR
        if self.NAQP or self.SPRINT:
            self.HISTORY = HIST_DIR+'NAQPCW.txt'
        elif self.CWops:
            self.KEYING=CWOPS_KEYING(self)
        elif self.SST:
            self.KEYING=SST_KEYING(self)
        elif self.CW_SS:
            self.HISTORY = HIST_DIR+'SS_Call_History_Aug2018.txt'
        elif self.CAL_QP:
            self.KEYING=CQP_KEYING(self)
        elif self.CW_OPEN:
            self.KEYING=CWOPEN_KEYING(self)
        elif self.ARRL_FD:
            #self.HISTORY = HIST_DIR+'FD_2020.txt'
            self.HISTORY = HIST_DIR+'FD_202*.txt'
        elif self.ARRL_VHF:
            self.KEYING=VHF_KEYING(self)
        elif self.SATELLITES:
            self.KEYING=SAT_KEYING(self)
        else:
            self.HISTORY = HIST_DIR+'master.csv'
            #self.HISTORY = ''
        if self.USE_MASTER:
            self.HISTORY = HIST_DIR+'master.csv'

        self.contest_name  = get_contest_name(self)
            
        self.ROTOR_CONNECTION = args.rotor
        self.PORT2            = args.port2

        # Read config file
        self.RCFILE=os.path.expanduser("~/.keyerrc")
        self.SETTINGS=None
        try:
            with open(self.RCFILE) as json_data_file:
                self.SETTINGS = json.load(json_data_file)
        except:
            print(self.RCFILE,' not found - need call!\n')
            s=SETTINGS(None,self)
            while not self.SETTINGS:
                try:
                    s.win.update()
                except:
                    pass
                time.sleep(.01)
            print('Settings:',self.SETTINGS)

        #sys,exit(0)

################################################################################

# Set up separate process that actualy does the keying.
# We do this so that the GUI process is not blocked by the keying.
def process_chars(P):
    last_time = 0
    keyer     = P.keyer
    lock      = P.lock1
    q         = P.q
    
    while not P.Stopper.isSet():

        # Anything available?
        if q.qsize()>0:
            txt=q.get()
            q.task_done()

            # Not sure whay this was here but it causes a problem when we get text from big box
            if P.PRACTICE_MODE and False:
                txt = ' '+txt

            # Check keyer speed on radio 
            this_time = time.time();
            if this_time - last_time>0.1 and not P.PRACTICE_MODE:
                last_time=this_time
                #WPM = socket_io.read_speed(P.sock)
                #print('PROCESS_CHARS: Reading speed')
                WPM = P.sock.read_speed()
                if WPM!=int( P.gui.WPM_TXT.get() ) and WPM>=5:
                    keyer.set_wpm(WPM)
                    P.gui.WPM_TXT.set(str(WPM))

            print('PROCESSS_CHARS: txt=',txt,'\tWPM=',keyer.WPM)

            # Timing is critical so we make sure we have control
            #if P.SIDETONE and not P.PRACTICE_MODE:
            if not P.PRACTICE_MODE:
                print('=========================================')
                P.q2.put(txt)
            lock.acquire()
            keyer.send_msg(txt)
            lock.release()

        else:
            
            if P.NANO_IO:
                
                if ser.in_waiting>0:
                    txt=nano_read(ser)
                    if False:
                        # Put it in the big text box also
                        P.gui.txt.insert(END, txt+'\n')
                        P.gui.txt.see(END)
                        P.gui.root.update_idletasks()
                else:
                    time.sleep(0.1)
                    
            else:
                time.sleep(0.1)
        
    print('PROCESSS_CHARS Done.')



def sidetone_executive(P):
    print('SIDETONE Exec')
    q = P.q2

    while not P.Stopper.isSet():
        if q.qsize()>0:
            msg = q.get()
            q.task_done()
            msg = msg.replace('[LOG]','')
            print('SIDETONE Exec: msg=',msg)
            P.osc.send_cw(msg,P.keyer.WPM,P.SIDETONE)
        else:
            time.sleep(0.1)
                
    print('SIDETONE Done.')
        
        
def WatchDog(P):
    #print('Watch Dog ....')

    # Check if another thread shut down - this isn't complete yet
    if P.SHUTDOWN:
        if P.CAPTURE:
            P.rec.stop_recording()
            P.rec.close()
        if P.Timer:
            print('WatchDog - Cancelling timer ...')
            P.Timer.cancel()
        #P.gui.Quit()
        P.WATCHDOG = False
        P.Timer=None
        print('WatchDog - Shut down.')

    # Read radio status
    if P.sock.connection!='NONE':
        print('Watch Dog - reading radio status ...', P.sock.connection)
        if False:
            socket_io.read_radio_status(P.sock)
            #print('\tWoof Woof:',P.sock.freq, P.sock.band, P.sock.mode, P.sock.wpm)
            
            P.gui.rig.band.set(P.sock.band)
            x=str(int(P.sock.freq*1e-3))+' KHz  '+str(P.sock.mode)
            P.gui.rig.status.set(x)
            P.gui.rig.frequency=P.sock.freq
            P.gui.rig.mode.set(P.sock.mode)
            #self.ant.set(ant)
            #print('\tWoof Woof 2:',x)

            if P.sock.mode=='FM':
                gui_tone = P.gui.rig.SB_PL_TXT.get()
                print('\tWoof Woof - PL tone=',P.sock.pl_tone,gui_tone)
                if P.sock.pl_tone==0:
                    tone='None'
                else:
                    tone=str(P.sock.pl_tone)
                if tone!=gui_tone:
                    #print('*** Tone Mismatch ***')
                    P.gui.rig.SB_PL_TXT.set(tone)

        else:
            freq = P.sock.get_freq()
            mode = P.sock.get_mode()
            band = P.sock.get_band(freq * 1e-6)

            P.gui.rig.band.set(band)
            x=str(int(freq*1e-3))+' KHz  '+str(mode)
            P.gui.rig.status.set(x)
            P.gui.rig.frequency=freq
            P.gui.rig.mode.set(mode)
            

    # Let user adjust WPM from radio knob
    if VERBOSITY>0:
        print("WatchDog - Checking WPM ...")
    if False:
        wpm=P.sock.wpm
    else:
        wpm = P.sock.read_speed()
    if wpm!=P.WPM and wpm>0:
        print("WatchDog - Changing WPM to",wpm)
        P.keyer.set_wpm(wpm)
        P.gui.WPM_TXT.set(str(wpm))
        P.WPM = wpm

    # Save program state to disk
    #print("WatchDog - Dirty Dozen ...")
    if P.DIRTY:
        P.gui.SaveState()

    # Compute QSO Rate
    if VERBOSITY>0:
        print("WatchDog - QSO Rate ...")
    P.gui.qso_rate()

    # Send out heart beat
    if P.UDP_SERVER:
        P.udp_server.Broadcast('Keyer Heartbeat - Thump Thump - kerr chunk')
    
    # Read rotor position
    #print('sock2=',P.sock2)
    #print('sock2=',P.sock2.connection)
    if P.sock2.connection!='NONE' or False:
        gui2=P.gui.rotor_ctrl
        pos=P.sock2.get_position()
        #print('pos:',pos)
        if pos[0]==None:
            pos[0]=gui2.azlcd1.get()             # Temp
        if pos[0]!=None:
            if pos[0]>180:
                pos[0]-=360
            if pos[0]<-180:
                pos[0]+=360
            gui2.azlcd1.set(pos[0])
            gui2.ellcd1.set(pos[1])
            gui2.nominalBearing()
    
    # Reset timer
    if VERBOSITY>0:
        print("WatchDog - Timer ...")
    if not P.gui.Done and not P.SHUTDOWN and not P.Stopper.isSet():
        P.Timer = threading.Timer(1.0, WatchDog, args=(P,))
        P.Timer.setDaemon(True)                       # This prevents timer thread from blocking shutdown
        P.Timer.start()
    else:
        P.Timer=None
        print('... Watch Dog quit')
        P.WATCHDOG = False

        
        
class serial_dummy():
    def __init__(self):
        print('Serial dummy object substituted')
        return

    def setDTR(self,a):
        return

def toggle_dtr(n=1):
        print('Toggling DTR ...')
        for i in range(n):
            time.sleep(1)
            print('DTR on')
            ser.setDTR(True)
            
            time.sleep(1)
            print('DTR off')
            ser.setDTR(False)
            
        #sys.exit(0)



def UDP_msg_handler(msg):
    print('UDP Message Handler: msg=',msg)
    self=P.gui

    if msg[:5]=='Call:':
        call=msg[5:]
        #print('UDP Message Handler: Setting call to:',call,P.gui.contest)
        call2=self.get_call()
        if call!=call2:
            self.Clear_Log_Fields()
            #self.call.delete(0, END)
            self.call.insert(0,call)
            self.dup_check(call)
            if P.gui.contest:
                #print('UDP Message Handler: Update hints')
                self.get_hint(call)
        
    
    
############################################################################################

print("\n\n***********************************************************************************")
print("\nStarting pyKeyer  ...")
P=PARAMS()
if True:
    print("P=")
    pprint(vars(P))
    print(' ')

# Open connection to rig
P.sock = socket_io.open_rig_connection(P.connection,0,P.PORT,0,'KEYER',rig=P.rig,force=P.FORCE)
if not P.sock.active and not P.PRACTICE_MODE:
    print('*** No connection available to rig ***')
    print('Perhaps you want practice mode?\n')
    sys.exit(0)

# Open keying control port
print('Opening keying port ...',P.sock.rig_type,P.sock.rig_type2)
if P.NANO_IO:
    try:
        ser = open_nano(baud=BAUD)
    except Exception as e: 
        print('\n*** Unable to open nano IO device ***\n')
        print( str(e) )
        sys.exit(0)
    P.ser=ser

#elif P.sock.rig_type=='Kenwood'  or (P.sock.rig_type=='Hamlib' and P.sock.rig_type2=='TS850'):
elif P.sock.rig_type2=='TS850':
    if P.PRACTICE_MODE and False:
        ser=serial_dummy()
    elif P.sock.connection=='DIRECT':
        ser = P.sock.s
    else:
        ser = serial.Serial(SERIAL_PORT5,4800,timeout=0.1)
        
    ser.setDTR(False)
    #toggle_dtr(5)
    #sys.exit(0)
        
elif P.sock.rig_type=='Icom' or (P.sock.rig_type=='Hamlib' and P.sock.rig_type2=='IC9700'):

    if P.PRACTICE_MODE:
        ser=serial_dummy()
    #elif P.sock.connection=='DIRECT' and False:
    #ser = P.sock.s
    
    elif P.sock.rig_type2=='IC9700':
        # If direct connect, could use USB A ...
        #ser = P.sock.s
        # but, in general, we'll use USB B in case we are using hamlib for rig control
        ser = serial.Serial(SERIAL_PORT10,BAUD,timeout=0.1,dsrdtr=0,rtscts=0)
        P.sock.init_keyer()
        time.sleep(.02)
        ser.setDTR(False)
        ser.setRTS(False)  
        
    else:
        # DTR keying does not work for the IC706
        # Instead, we need to connect the TS850 interface to the keying line
        # It looks like DTR keying is supported by the IC9700 - needs work
        
        print('Opening keying port on IC706 ...')
        ser = serial.Serial(SERIAL_PORT5,19200,timeout=0.1)
        ser.setDTR(False)
        print('... Opened keying port on IC706 ...')

    if False:
        toggle_dtr()
        
else:

    if not P.PRACTICE_MODE:

        if P.sock.rig_type2=='FT991a':
            ser = serial.Serial(SERIAL_PORT4,BAUD,timeout=0.1,dsrdtr=0,rtscts=0)
            ser.setDTR(True)
            time.sleep(.02)
            ser.setDTR(False)
            ser.setRTS(False)                       # Digi mode uses this for PTT?

            if P.sock.connection=='DIRECT' or True:
                # This type of command doesn't work for most versions of hamlib
                cmd = 'BY;EX0603;EX0561;'               # Set DTR keying and full QSK
                buf=P.sock.get_response(cmd)
            
            ser.PORT = SERIAL_PORT4
            ser.BAUD = BAUD

            if False:
                print('buf=',buf)
                time.sleep(1)
                print('DTR off')
                ser.setDTR(False)
                time.sleep(1)
                print('DTR on')
                ser.setDTR(True)
                time.sleep(1)
                print('DTR off')
                ser.setDTR(False)
                time.sleep(1)
                sys.exit(0)
            
        elif P.sock.rig_type2=='FTdx3000':
            ser = serial.Serial(SERIAL_PORT2,BAUD,timeout=0.1)
            ser.setDTR(False)
            ser.PORT = SERIAL_PORT2
            ser.BAUD = BAUD

        else:
            print('pyKeyer: Unknown rig type:',P.sock.rig_type,P.sock.rig_type2)
            sys.exit(0)
        
    else:
        print('### Unable to open serial port to rig ###')
        ser=serial_dummy()


# Put rig and FLDIGI into initial mode
if not P.PRACTICE_MODE:
    print('Initial mode=',P.INIT_MODE)
    P.sock.set_mode(P.INIT_MODE,VFO='A')
    split = P.sock.split_mode(-1)
    if split:
        P.sock.set_mode(P.INIT_MODE,VFO='B')
    #sys.exit(0)

# Open connection to rotor
P.sock2 = socket_io.open_rig_connection(P.ROTOR_CONNECTION,0,P.PORT2,0,'ROTOR')
if not P.sock2.active and P.sock2.connection!='NONE':
    print('*** No connection available to rotor ***')
    sys.exit(0)

# Open connection to FLLOG, if available
P.sock3 = socket_io.open_rig_connection('FLLOG',0,0,0,'KEYER')
#print(P.sock3.active)

# Create hamlib-like server for clients like SDR to talk through
P.threads=[]
P.SO2V=False
P.NUM_RX=0
P.Stopper = threading.Event()
if not P.PRACTICE_MODE and P.sock.connection!='HAMLIB' and P.HAMLIB_SERVER:
    for port in [4532, 4632]:
        #th = threading.Thread(target=rigctl.HamlibServer(P,HAMLIB_PORT).Run, args=(),name='Hamlib Server')
        th = threading.Thread(target=rigctl.HamlibServer(P,port).Run, args=(),name='Hamlib Server')
        th.setDaemon(True)
        th.start()
        P.threads.append(th)

# Instaniate the keyer
if P.WPM==0:
    #wpm = socket_io.read_speed(sock)
    wpm = P.sock.read_speed()
else:
    wpm = P.WPM
    print('Init WPM to',wpm,'...')
    #socket_io.set_speed(P.sock,wpm)
    P.sock.set_speed(wpm)

P.keyer=cw_keyer.Keyer(P,ser,wpm)
if P.TEST_MODE:
    P.keyer.disable()           # Disable TX keying for debugging

# Create sidetone oscillator
P.osc = SIDETONE_OSC(P.keyer.WPM,AMP,F0,FS)
P.keyer.sidetone = P.osc

# We need a queue for sending messages to the keying thread
# and a locks to coordinate time-critical sections of the keying & practice
# threads
if sys.version_info[0]==3:
    P.q     = queue.Queue(maxsize=0)
else:
    P.q     = Queue.Queue(maxsize=0)
P.lock1 = threading.Lock()
#P.lock2 = threading.Lock()
P.keyer.evt =  threading.Event()
P.keyer.evt.clear()

# Start a thread that controls keying of TX
worker = threading.Thread(target=process_chars, args=(P,),name='Process Chars')
worker.setDaemon(True)
worker.start()
P.threads.append(worker)

# Start listener in a separate thread - not sure if we really use anymore
if False:
    server = threading.Thread(target=cw_keyer.cw_server, \
                              args=(P,HOST,KEYER_PORT),name='CW Server')
    server.setDaemon(True)
    server.start()
    P.threads.append(server)

# Start sidetone osc in a separate thread
if sys.version_info[0]==3:
    P.q2     = queue.Queue(maxsize=0)
else:
    P.q2     = Queue.Queue(maxsize=0)
sidetone = threading.Thread(target=sidetone_executive, args=(P,),name='Sidetone Osc')
sidetone.setDaemon(True)
sidetone.start()
P.threads.append(sidetone)

# Load history from previous contests
if P.USE_MASTER:
    print('Loading Master History file ...')
    P.MASTER = load_history(HIST_DIR+'master.csv')
else:
    P.MASTER = {}
P.calls = list(P.MASTER.keys())

# Create GUI
P.gui     = GUI(P,MACROS)

# Set up a thread for code practice
P.practice = practice.CODE_PRACTICE(P)
worker = threading.Thread(target=P.practice.run, args=(), name='Practice Exec' )
worker.setDaemon(True)
worker.start()
P.threads.append(worker)

# Start thread with UDP server
if P.UDP_SERVER:
    P.udp_server = TCP_Server(None,7474,Stopper=P.Stopper,Handler=UDP_msg_handler)
    worker = Thread(target=P.udp_server.Listener, args=(), name='UDP Server' )
    worker.setDaemon(True)
    worker.start()
    P.threads.append(worker)

# WatchDog - runs in its own thread
P.WATCHDOG = True
#P.WATCHDOG = False
if P.WATCHDOG:
    P.Timer = threading.Timer(1.0, WatchDog, args=(P,))
    P.Timer.setDaemon(True)                       # This prevents timer thread from blocking shutdown
    P.Timer.start()
else:
    P.Timer = None

# Init rig to useful settings    
if P.sock.active:
    # Set TX power
    P.sock.set_power(99)

    # Set sub-dial
    P.sock.set_sub_dial('CLAR')
    
# Spin
mainloop()

