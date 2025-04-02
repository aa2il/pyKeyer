################################################################################
#
# Keying.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
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
import os
from nano_io import *
from utilities import list_all_serial_devices,error_trap, get_PIDs,find_serial_device,find_serial_device_by_serial_id
from rig_io import BAUD,SERIAL_PORT2,SERIAL_PORT4

from tkinter import messagebox

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

def find_keyer(P):

    DEVICES   = ['WINKEYER','NANO IO','K3NG']
    BAUDS     = [1200,NANO_BAUD,NANO_BAUD]
    CMDS      = [chr(0)+chr(2),'~?','\\?']
    RESPONSES = [chr(0x17),'nanoIO ver','K3NG Keyer']

    KEYER_DEVICE    = P.SETTINGS["MY_KEYER_DEVICE"]
    KEYER_DEVICE_ID = P.SETTINGS["MY_KEYER_DEVICE_ID"]

    print('\nFIND KEYER: Looking for keyer device ...')
    print('\tKEYER_DEVICE    =',KEYER_DEVICE)
    print('\tKEYER_DEVICE_ID =',KEYER_DEVICE_ID)
    print('\tKEYER_PORT      =',P.KEYER_PORT)
    if KEYER_DEVICE_ID=='':
        print('\n*** Fatal Error *** Need to set MY_KEYER_DEVICE_ID ',
              'in ~/.keyerrc so we can find the keyer port :-(\n')
        print('\nThese are the USB devices available:')
        list_all_serial_devices(True)
        sys.exit(0)

    # There are a couple of ways to find the device - need to figure out what will work with winbloz
    list_all_serial_devices(USB_ONLY=True)
    device,vid_pid=find_serial_device(KEYER_DEVICE_ID,0,VERBOSITY=2,PORT=P.KEYER_PORT)
    print('\tkeyer device=',device,'\tvid_pid=',vid_pid)
    
    if not device:
        print('... Not found - Looking for ESP32 keyer device ...')
        device,vid_pid=find_serial_device('nanoIO32',0,VERBOSITY=2)
        print('\tdevice=',device)
    if device:
        print(' ... There it is on port',device,' ...\n')
        set_DTR_hangup(device,False)
        #set_DTR_hangup(device,True)
        #sys.exit(0)

        # Forget the search until we get the winkeyer working for Lloyd
        if len(KEYER_DEVICE)==0:
            KEYER_DEVICE='WINKEYER'
        if len(KEYER_DEVICE)>0:
            return device,KEYER_DEVICE,vid_pid
    else:
        print('\nNo serial keyer device found\n')
        return None,None,None
    
    for i in range(len(DEVICES)):
        print('\nFIND KEYER: Looking for',DEVICES[i],'device ...')
        
        baud=BAUDS[i]
        ser = serial.Serial(device,baud,timeout=1,
                            xonxoff=False,dsrdtr=False,rtscts=False)
        print('\tser=',ser)
        time.sleep(.1)
        ser.reset_input_buffer()

        #time.sleep(.1)
        #ser.reset_input_buffer
        #ser.reset_output_buffer
        #time.sleep(.1)

        cnt=ser.write(bytes(CMDS[i],'utf-8'))
        time.sleep(.1)
        txt2 = ser.read(256).decode("utf-8",'ignore')
        print('FIND KEYER: \tCMD=',show_hex(CMDS[i]),
              '\ntxt2=',txt2,'\ntxt2=',show_hex(txt2),
              '\tlen=',len(txt2))

        """
        if i==0 and len(txt2)==0 and False:
            print('Try again ...')
            time.sleep(5)
            cnt=ser.write(bytes(CMDS[i],'utf-8'))
            time.sleep(.1)
            txt2 = ser.read(256).decode("utf-8",'ignore')
            print('txt2=',txt2,'\n',show_hex(txt2),'\tlen=',len(txt2))
        """

        ntries=1
        while len(txt2)==256 and ntries<10:
            ntries+=1
            print('Try again - ',ntries,'of 10 ...')
            ser.close()
            time.sleep(.1)
            ser.open()
            time.sleep(.1)
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            time.sleep(.1)
        
            txt2 = ser.read(256).decode("utf-8",'ignore')
            print('txt2=',txt2,'\n',show_hex(txt2),'\tlen=',len(txt2))
        
        if RESPONSES[i] in txt2:
            print('Found',DEVICES[i],'Device')
            return device,DEVICES[i],vid_pid

        ser.close()
        
    return device,None,vid_pid

################################################################################

# Function to open keying control port
def open_keying_port(P,sock,rig_num):
    if not sock:
        return None

    vid_pid=None
    
    print('\nOpening keying port ... USE_KEYER=',P.USE_KEYER,'\trig_num=',rig_num)
    print('\tFIND_KEYER=',P.FIND_KEYER)
    print('\tKEYER_PORT=',P.KEYER_PORT)
    if P.gui:
        P.gui.status_bar.setText("Opening Keying Port ...")

    if P.USE_KEYER and rig_num==1:
        if P.FIND_KEYER or P.KEYER_PORT!=None:
            
            device,dev_type,vid_pid=find_keyer(P)
            print('device=',device,'\tdev_type=',dev_type)
            Done = dev_type!=None
            while not Done:
                print('\nOPEN_LEYING_PORT: Unable to find keyer device!')
                
                pids = get_PIDs('pyKeyer.py') + get_PIDs('paddling.py')
                print('\npids=',pids)
                if len(pids)>1:
                    print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                    print(  "@ Try killing other instances of this program! @")
                    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
                else:
                    print("\n@@@@@@@@@@@@@@@@@@@@@@@@")
                    print(  "@ Is it plugged in ??? @")
                    print(  "@@@@@@@@@@@@@@@@@@@@@@@@\n")

                # Let's see if another process is using the keyer
                if True:
                    print('\nChecking device usage ...')
                    cmd="lsof "+device
                    print('\tcmd=',cmd)
                    os.system(cmd)                    

                result = try_usb_reset(P,vid_pid)
                
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
            print('OPEN KEYING PORT: device=',device,'\tprotocol=',protocol)
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

            pids = get_PIDs('pyKeyer.py') + get_PIDs('paddling.py')
            print('\npids=',pids)
            if len(pids)>0:
                print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                print(  "@ Try killing other instances of this program! @")
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")

            result=try_usb_reset(P,vid_pid)
            if result:
                print('keyer_device=',P.keyer_device)
                ser = P.keyer_device.ser
                print('ser=',ser)
            else:
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
                port,vid_pid=find_serial_device(sock.rig_type2,1,VERBOSITY=1)
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
                
                port,vid_pid=find_serial_device('FT991a',1,VERBOSITY=1)
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

                port,vid_pid=find_serial_device('FTdx3000',1,VERBOSITY=1)
                ser = serial.Serial(port,BAUD,timeout=0.1)
                ser.setDTR(False)
                ser.PORT = SERIAL_PORT2
                ser.BAUD = BAUD

            elif sock.rig_type2 in ['None','TYT9000d','Hamlib','FLDIGI']:
                ser=serial_dummy()

            else:
                print('KEYING - OPEN KEYING PORT: Unknown rig type:',sock.rig_type,sock.rig_type1,sock.rig_type2)
                sys.exit(0)
        
        else:
            print('### Unable to open serial port to rig ###')
            ser=serial_dummy()

    return ser

        

def try_usb_reset(P,vid_pid):
    
    print('\nTRY USB RESET: vid_pid=',vid_pid)
    
    msg='Try Resetting USB Bus?'
    lab="pyKeyer"
    if P.gui:
        P.gui.splash.hide()
    #result=messagebox.askyesno(lab,msg)
    result=messagebox.askyesnocancel(lab,msg)
    if result==True:
        cmd="sudo usbreset "+vid_pid
        print('\tcmd=',cmd)
        os.system(cmd)                    
        Done = False
        #sys.exit(0)
    elif result==False:
        device,dev_type,vid_pid=find_keyer(P)
        print('device=',device,'\tdev_type=',dev_type)
        Done = dev_type!=None
        if P.gui:
            P.gui.splash.show()
    else:
        print('Giving up!')
        Done = True
        sys.exit(0)
                    
    return Done        # ,device,dev_type,vid_pid
