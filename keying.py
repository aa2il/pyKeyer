#! /usr/bin/python3 -u
################################################################################
#
# Keying.py - Rev 1.0
# Copyright (C) 2021-4 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines relating to keying the rig.
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
from nano_io import *
from utilities import error_trap, get_PIDs
from rig_io import BAUD,SERIAL_PORT4

################################################################################

class serial_dummy():
    def __init__(self):
        print('Serial dummy object substituted')
        self.out_waiting=0
        return

    def setDTR(self,a):
        return

    def write(self,a=None,b=None):
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

################################################################################

def find_keyer():

    DEVICES   = ['NANO IO','K3NG','WINKEYER']
    BAUDS     = [NANO_BAUD,NANO_BAUD,1200]
    CMDS      = ['~?','\\?',chr(0)+chr(2)]
    RESPONSES = ['nanoIO ver','K3NG Keyer',chr(0x17)]

    print('\nFIND KEYER: Looking for nanoIO keyer device ...')
    device=find_serial_device('nanoIO',0,2)
    print('FIND KEYER: device=',device)
    if not device:
        print('... Not found - Looking for ESP32 keyer device ...')
        device=find_serial_device('nanoIO32',0,2)
        print('device=',device)
    if device:
        print(' ... There it is on port',device,' ...\n')
        set_DTR_hangup(device,False)
        #set_DTR_hangup(device,True)
    else:
        print('\nNo serial keyer device found\n')
        return None,None
    
    for i in range(len(DEVICES)):
        print('Looking for',DEVICES[i],'device ...')
        
        baud=BAUDS[i]
        ser = serial.Serial(device,baud,timeout=1,
                            xonxoff=False,dsrdtr=False,rtscts=False)
        print('FIND KEYER: ser=',ser)

        #time.sleep(.1)
        #ser.reset_input_buffer
        #ser.reset_output_buffer
        #time.sleep(.1)
        
        cnt=ser.write(bytes(CMDS[i],'utf-8'))
        #print('cnt=',cnt)
        time.sleep(.1)
        txt2 = ser.read(256).decode("utf-8",'ignore')
        print('FIND KEYER: txt2=',txt2,'\ntxt2=',show_hex(txt2),
              '\tlen=',len(txt2),'\tCMD=',show_hex(CMDS[i]))

        """
        if i==0 and len(txt2)==0 and False:
            print('Try again ...')
            time.sleep(5)
            cnt=ser.write(bytes(CMDS[i],'utf-8'))
            time.sleep(.1)
            txt2 = ser.read(256).decode("utf-8",'ignore')
            print('txt2=',txt2,'\n',show_hex(txt2),'\tlen=',len(txt2))

        ntries=1
        while len(txt2)==256 and ntries<10:
            ntries+=1
            print('Try again ...')
            ser.close()
            time.sleep(.1)
            ser.open()
            time.sleep(.1)
            ser.reset_input_buffer
            ser.reset_output_buffer
            time.sleep(.1)
        
            txt2 = ser.read(256).decode("utf-8",'ignore')
            print('txt2=',txt2,'\n',show_hex(txt2),'\tlen=',len(txt2))
        """
        
        if RESPONSES[i] in txt2:
            print('Found',DEVICES[i],'Device')
            return device,DEVICES[i]

        ser.close()
        
    return device,None

################################################################################

# Function to open keying control port
def open_keying_port(P,sock,rig_num):
    if not sock:
        return None
    
    print('Opening keying port ...')   # ,sock.rig_type,sock.rig_type2)
    if P.USE_KEYER and rig_num==1:
        if P.FIND_KEYER:
            
            device,dev_type=find_keyer()
            print('device=',device,'\tdev_type=',dev_type)
            if dev_type==None:
                print('\nUnable to find keyer device - giving up!')
                
                pids = get_PIDs('pyKeyer.py')
                print('pids=',pids)
                if len(pids)>1:
                    print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                    print(  "@ Try killing other instances of this program! @")
                    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
                else:
                    print("\n@@@@@@@@@@@@@@@@@@@@@@@@")
                    print(  "@ Is it plugged in ??? @")
                    print(  "@@@@@@@@@@@@@@@@@@@@@@@@\n")
            
                sys.exit(0)
            else:
                P.NANO_IO  = dev_type=='NANO IO'
                P.K3NG_IO  = dev_type=='K3NG'
                P.WINKEYER = dev_type=='WINKEYER'
                time.sleep(.1)

        else:
            
            device=None
            
        try:
            FATAL_ERROR=False
            if P.NANO_IO:
                protocol='NANO_IO'
                BAUD_KEYER=NANO_BAUD
            elif P.K3NG_IO:
                protocol='K3NG_IO'
                BAUD_KEYER=NANO_BAUD
            elif P.WINKEYER:
                protocol='WINKEYER'
                BAUD_KEYER=1200
            else:
                print('OPEN KEYING PORT - Unknown protocol')
                sys.exit(0)
            P.keyer_device = KEYING_DEVICE(P,device,protocol,baud=BAUD_KEYER)
            ser = P.keyer_device.ser
        except: 
            error_trap('KEYING->OPEN KEYING PORT',1)
            print('\n*************************************')
            print(  '*** Unable to open Nano IO device ***')
            print(  '***  Make sure it is plugged in   ***')
            print(  '***  and that no app is using it  ***')
            print(  '*************************************')
            print(  '***          Giving up            ***')
            print('*************************************\n')

            pids = get_PIDs('pyKeyer.py')
            print('pids=',pids)
            if len(pids)>0:
                print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                print(  "@ Try killing other instances of this program! @")
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
            FATAL_ERROR=True

        if FATAL_ERROR:
            sys.exit(0)

            
    elif sock.rig_type2=='TS850':
        if P.PRACTICE_MODE and False:
            ser=serial_dummy()
        elif sock.connection=='DIRECT':
            ser = sock.s
        else:
            ser = serial.Serial(SERIAL_PORT5,4800,timeout=0.1)
        
        ser.setDTR(False)
        #toggle_dtr(5)
        #sys.exit(0)
        
    elif sock.rig_type=='Icom' or \
         (sock.rig_type=='Hamlib' and sock.rig_type2 in ['IC9700','IC7300']) or \
         (sock.rig_type=='FLRIG'  and sock.rig_type2 in ['IC9700','IC7300']):

        if P.PRACTICE_MODE:
            ser=serial_dummy()
    
        elif sock.rig_type2 in ['IC9700','IC7300']:
            # If direct connect, could use USB A ...
            #ser = P.sock.s
            # but, in general, we'll use USB B in case we are using hamlib for rig control
            #print('OPEN KEYING PORT:',SERIAL_PORT10,BAUD)
            try:
                port=find_serial_device(sock.rig_type2,1,VERBOSITY=1)
                ser = serial.Serial(port,BAUD,timeout=0.1,dsrdtr=0,rtscts=0)
                print('OPEN KEYING PORT: Sock Init...')
                sock.init_keyer()
                time.sleep(.1)
                ser.setDTR(False)
                ser.setRTS(False)  
                time.sleep(1)
                ser.setDTR(False)
                ser.setRTS(False)  
            except: 
                error_trap('KEYING->OPEN KEYING PORT')
                print('\n*************************************')
                print('Unable to open keying port for rig',rig_num)
                print('*************************************')
                ser=None
                sys.exit(0)
        
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

            if sock.rig_type2=='FT991a':
                
                port=find_serial_device('FT991a',1,VERBOSITY=1)
                ser = serial.Serial(port,BAUD,timeout=0.1,dsrdtr=0,rtscts=0)
                ser.setDTR(True)
                time.sleep(.02)
                ser.setDTR(False)
                ser.setRTS(False)                       # Digi mode uses this for PTT?

                if sock.connection=='DIRECT' or True:
                    # This type of command doesn't work for most versions of hamlib
                    cmd = 'BY;EX0603;EX0561;'               # Set DTR keying and full QSK
                    buf=sock.get_response(cmd)
            
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
                    
            elif sock.rig_type2=='FTdx3000':

                port=find_serial_device('FTdx3000',1,VERBOSITY=1)
                ser = serial.Serial(port,BAUD,timeout=0.1)
                ser.setDTR(False)
                ser.PORT = SERIAL_PORT2
                ser.BAUD = BAUD

            elif sock.rig_type2 in ['None','TYT9000d']:
                ser=serial_dummy()

            else:
                print('KEYING - OPEN KEYING PORT: Unknown rig type:',sock.rig_type,sock.rig_type2)
                sys.exit(0)
        
        else:
            print('### Unable to open serial port to rig ###')
            ser=serial_dummy()

    return ser

        
