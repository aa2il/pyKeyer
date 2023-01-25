#! /usr/bin/python3 -u
################################################################################
#
# pyKeyer.py - Rev 1.0
# Copyright (C) 2021-3 by Joseph B. Attili, aa2il AT arrl DOT net
#
#    Main program for CW Keyer and server.
#
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
import xlrd
from latlon2maiden import *
from watchdog import *
from keying import *
from process_chars import *
from tcp_server import *
from udp import *

################################################################################

VERSION='1.01'

################################################################################

print("\n\n***********************************************************************************")
print("\nStarting pyKeyer v'+VERSION+' ...")
P=PARAMS()
if True:
    print("P=")
    pprint(vars(P))
    #sys.exit(0)
    
# Initialize GUI
P.gui     = GUI(P)
    
# Open connection to 1st rig
print('\nPYKEYER: Opening connection to primary rig - connection=',
      P.connection,'\trig=',P.rig,'...')
P.sock1 = socket_io.open_rig_connection(P.connection,0,P.PORT,0,'KEYER',
                                        rig=P.rig,force=P.FORCE)
#sys.exit(0)
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
print('P.sock1=',P.sock1,P.sock1.rig_type,P.sock1.rig_type1,P.sock1.rig_type2)

# Open connection to 2nd rig
if P.connection2 != "NONE":
    print('\nPYKEYER: Opening connection to secondary rig - connection=',P.connection2,'\trig=',P.rig2,'...')
    P.sock2 = socket_io.open_rig_connection(P.connection2,0,P.PORT2,0,'KEYER',rig=P.rig2,force=P.FORCE)
else:
    P.sock2=None
#print('P.sock2=',P.sock2,P.sock2.rig_type,P.sock2.rig_type1,P.sock2.rig_type2)
#sys.exit(0)

# Open connection to 3rd rig
if P.connection3 != "NONE":
    print('\nPYKEYER: Opening connection to terciary rig - connection=',P.connection3,'\trig=',P.rig3,'...')
    P.sock3 = socket_io.open_rig_connection(P.connection3,0,P.PORT3,3,'KEYER',rig=P.rig3,force=P.FORCE)
else:
    P.sock3=None
#print('P.sock3=',P.sock3,P.sock3.rig_type,P.sock3.rig_type1,P.sock3.rig_type2)
#sys.exit(0)

# Check if we need nano device
if P.SENDING_PRACTICE and not P.NANO_IO:
    print('\n*******************************************************')
    print('*******************************************************')
    print('*** We need the NANO IO device for sending practice ***')
    print('*******************************************************')
    print('*******************************************************')
    sys.exit(1)

# Open keying port(s)
P.ser1=open_keying_port(P,P.sock1,1)
P.ser2=open_keying_port(P,P.sock2,2)
P.ser3=open_keying_port(P,P.sock3,2)
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
P.sock_rotor = socket_io.open_rig_connection(P.ROTOR_CONNECTION,0,P.PORT9,0,'ROTOR')
if not P.sock_rotor.active and P.sock_rotor.connection!='NONE':
    print('*** No connection available to rotor ***')
    sys.exit(0)

    
# Experiemtnal area - starting to get FLRIG's CWIO interface up & running - in progress
if False:
    print('Howdy Ho!',P.sock.cwio_get_wpm())
    P.sock.cwio_set_wpm(25)
    print('Howdy Ho Agn!',P.sock.cwio_get_wpm())
    P.sock.cwio_write('test')
    time.sleep(5)
    sys.exit(0)

    
# Open connection to FLLOG, if available
P.sock_log = socket_io.open_rig_connection('FLLOG',0,0,0,'KEYER')
#print(P.sock_log.active)

# Create hamlib-like server for clients like SDR to talk through
P.threads=[]
P.SO2V=False
P.NUM_RX=0
P.Stopper = threading.Event()
if not P.PRACTICE_MODE and P.sock.connection!='HAMLIB' and P.HAMLIB_SERVER:
    print('Creating HAMLIB servers ...')
    for port in [4532, 4632]:
        th = threading.Thread(target=rigctl.HamlibServer(P,port).Run, args=(),name='Hamlib Server')
        th.daemon=True
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

P.keyer=cw_keyer.Keyer(P,wpm)
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
worker.daemon=True
worker.start()
P.threads.append(worker)

# Start listener in a separate thread - not sure if we really use anymore
if False:
    print('Creating Listener thread ...')
    server = threading.Thread(target=cw_keyer.cw_server, \
                              args=(P,HOST,KEYER_PORT),name='CW Server')
    server.daemon=True
    server.start()
    P.threads.append(server)

# Create sidetone oscillator & start in a separate thread
print('Creating Sidetone ...')
#init_sidetone(P)
P.SideTone = AUDIO_SIDETONE(P)

# Set up a thread for audio capture
if P.CAPTURE or True:
    print('Creating thread to Capture Audio ...')
    P.capture = audio_capture.AUDIO_CAPTURE(P)
    worker = threading.Thread(target=P.capture.run, args=(), name='Capture Exec' )
    worker.daemon=True
    worker.start()
    P.threads.append(worker)

# Load history from previous contests
print('Loading Master History file ...')
P.MASTER,fname9 = load_history(P.HIST_DIR+'master.csv')
P.calls = list(P.MASTER.keys())
print('... Info for',len(P.calls),'calls were loaded.')

# Actually create the GUI
P.gui.construct_gui()

# Set up a thread for code practice
print('Creating Practice Exec thread ...')
P.practice = practice.CODE_PRACTICE(P)
worker = threading.Thread(target=P.practice.run, args=(), name='Practice Exec' )
worker.daemon=True
worker.start()
P.threads.append(worker)

# Start thread with UDP server
if P.UDP_SERVER:
    P.udp_server = TCP_Server(P,None,KEYER_UDP_PORT,Server=True,
                              Handler=UDP_msg_handler)
    worker = Thread(target=P.udp_server.Listener, args=(), name='UDP Server' )
    worker.daemon=True
    worker.start()
    P.threads.append(worker)

# WatchDog - runs in its own thread
P.WATCHDOG = True
if P.WATCHDOG:
    P.Timer = threading.Timer(1.0, WatchDog, args=(P,))
    P.Timer.daemon=True                       # This prevents timer thread from blocking shutdown
    P.Timer.start()
else:
    P.Timer = None

# Init rig to useful settings    
if P.sock.active:
    print('PYKEYER - Init rig ...')
    
    # Set TX power
    P.sock.set_power(99)

    # Set sub-dial
    P.sock.set_sub_dial('CLAR')

    # Set freq to CW band
    if True:
        print('PYKEYER - Set freq ...')
        frq  = 1e-3*P.sock.get_freq() 
        band = freq2band(1e-3*frq)
        f1=bands[band]['CW1']
        f2=bands[band]['CW2']
        print('PYKEYER - Set freq ... current frq=',frq,'\tBand:',band,f1,f2)
        if P.contest_name in ['CWT','MST','SST']:
            if frq>f1+50:
                print('PYKEYER - Setting freq to',f1+30)
                P.sock.set_freq(f1+30) 
        elif frq>f1+79:     # frq>0.5*(f1+f2):
            print('PYKEYER - BURP - Setting freq to',f1+30)
            P.sock.set_freq(f1+30) 

# Read satellite grids confirmed - this will be used to alert station in new grid
FNAME = P.HIST_DIR+'states.xls'
P.grids=[]
if os.path.isfile(FNAME):
    print('Reading Sat Grids - fname=',FNAME)
    book  = xlrd.open_workbook(FNAME,formatting_info=True)
    sheet1 = book.sheet_by_name('Satellites')

    # Digest confirmed grids
    for i in range(1, sheet1.nrows):
        #print(i,sheet1.cell(i,10) )
        grid = unidecode( sheet1.cell(i,3).value )
        if len(grid)>0 and 'Paper' not in grid:
            P.grids.append( grid.upper() )
    print('Grids:',P.grids)

# Start sidetone and capture audio processing
if P.SIDETONE or P.CAPTURE:
    print('Starting Sidetone ...')
    P.SideTone.start()
if P.CAPTURE:
    P.capture.start()

# Spin
mainloop()

