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
import re
import serial
import practice 
import audio_capture
import rig_io.socket_io as socket_io
import threading
if sys.version_info[0]==3:
    import queue
else:
    import Queue
from subprocess import call
from gui import *
from load_history import *
from pprint import pprint
import rig_io.hamlibserver as rigctl
from sidetone import *
import time
import os
from params import *
from settings import *
from tcp_server import *
import xlrd
from latlon2maiden import *
from watchdog import *
from keying import *
from process_chars import *

################################################################################

def UDP_msg_handler(msg):
    print('UDP Message Handler: msg=',msg)
    self=P.gui

    #idx = msg.count('Call:')
    idx = [m.start() for m in re.finditer('Call:', msg)]
    if len(idx)>0:
        call=msg[idx[-1]+5:]
        print('UDP Message Handler: Setting call to:',call,idx,P.gui.contest)
        call2=self.get_call()
        if call!=call2:
            self.Clear_Log_Fields()
            #self.call.delete(0, END)
            self.call.insert(0,call)
            self.dup_check(call)
            if P.gui.contest:
                #print('UDP Message Handler: Update hints')
                self.get_hint(call)
                if P.AUTOFILL:
                    P.KEYING.insert_hint()
        
    elif msg[:4]=='Sat:':
        sat=msg[4:]
        print('UDP Message Handler: Setting SAT to:',sat)
        self.set_satellite(sat)
    
############################################################################################

print("\n\n***********************************************************************************")
print("\nStarting pyKeyer  ...")
P=PARAMS()
if True:
    print("P=")
    pprint(vars(P))

# Initialize GUI
P.gui     = GUI(P)
    
# Open connection to 1st rig
print('\nPYKEYER: Opening connection to primary rig - connection=',P.connection,'\trig=',P.rig,'...')
P.sock1 = socket_io.open_rig_connection(P.connection,0,P.PORT,0,'KEYER',rig=P.rig,force=P.FORCE)
if not P.sock1.active and not P.PRACTICE_MODE:
    print('*** No connection available to rig ***')
    print('Perhaps you want practice mode?\n')
    if P.PLATFORM=='Linux' and True:
        sys.exit(0)
    else:
        # Windows - go into practice mode since we haven't got rig control working yet anyway
        P.gui.PracticeCB()
        P.SIDETONE=True
        
P.sock=P.sock1
print('P.sock1=',P.sock1)

# Open connection to 2nd rig
if P.connection2 != "NONE":
    print('\nPYKEYER: Opening connection to secondary rig - connection=',P.connection2,'\trig=',P.rig2,'...')
    P.sock2 = socket_io.open_rig_connection(P.connection2,0,P.PORT2,0,'KEYER',rig=P.rig2,force=P.FORCE)
else:
    P.sock2=None
print('P.sock2=',P.sock2)
#sys.exit(0)

# Open keying port(s)
P.ser1=open_keying_port(P,P.sock1,1)
P.ser2=open_keying_port(P,P.sock2,2)
P.ser=P.ser1
#sys.exit(0)
    
# Put rig and FLDIGI into initial mode
if not P.PRACTICE_MODE:
    print('Initial mode=',P.INIT_MODE)
    P.sock.set_mode(P.INIT_MODE,VFO='A')
    split = P.sock.split_mode(-1)
    if split:
        P.sock.set_mode(P.INIT_MODE,VFO='B')
    #sys.exit(0)

# Open connection to rotor
P.sock3 = socket_io.open_rig_connection(P.ROTOR_CONNECTION,0,P.PORT3,0,'ROTOR')
if not P.sock3.active and P.sock3.connection!='NONE':
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
    print('Creating HAMLIB servers ...')
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

P.keyer=cw_keyer.Keyer(P,P.ser,wpm)
if P.TEST_MODE:
    P.keyer.disable()           # Disable TX keying for debugging

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
print('Creating thread to Process Chars ...')
worker = threading.Thread(target=process_chars, args=(P,),name='Process Chars')
worker.setDaemon(True)
worker.start()
P.threads.append(worker)

# Start listener in a separate thread - not sure if we really use anymore
if False:
    print('Creating Listener thread ...')
    server = threading.Thread(target=cw_keyer.cw_server, \
                              args=(P,HOST,KEYER_PORT),name='CW Server')
    server.setDaemon(True)
    server.start()
    P.threads.append(server)

# Create sidetone oscillator & start in a separate thread
print('Creating Sidetone ...')
init_sidetone(P)

# Set up a thread for audio capture
print('Creating thread to Capture Audio ...')
P.capture = audio_capture.AUDIO_CAPTURE(P)
worker = threading.Thread(target=P.capture.run, args=(), name='Capture Exec' )
worker.setDaemon(True)
worker.start()
P.threads.append(worker)

# Load history from previous contests
if P.USE_MASTER:
    print('Loading Master History file ...')
    P.MASTER = load_history(P.HIST_DIR+'master.csv')
else:
    P.MASTER = {}
P.calls = list(P.MASTER.keys())

# Actually create the GUI
P.gui.construct_gui()

# Set up a thread for code practice
print('Creating Practice Exec thread ...')
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

# Read satellite grids confirmed - this will be used to alert station in new grid
FNAME = P.DATA_DIR+'states.xls'
print('Reading Sat Grids - fname=',FNAME)
book  = xlrd.open_workbook(FNAME,formatting_info=True)
sheet1 = book.sheet_by_name('6-meters')

# Digest confirmed grids
P.grids=[]
for i in range(1, sheet1.nrows):
    #print(i,sheet1.cell(i,10) )
    grid = unidecode( sheet1.cell(i,10).value )
    if len(grid)>0 and 'Paper' not in grid:
        P.grids.append( grid.upper() )
print('Grids:',P.grids)

#sys.exit(0)

# Spin
mainloop()

