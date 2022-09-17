#! /usr/bin/python3 -u
################################################################################
#
# Keying.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
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
from rig_io.ft_tables import *

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



# Function to open keying control port
def open_keying_port(P,sock,rig_num):
    if not sock:
        return None
    
    print('Opening keying port ...',sock.rig_type,sock.rig_type2)
    if P.NANO_IO and rig_num==1:
        try:
            ser = open_nano(baud=NANO_BAUD)
        except Exception as e: 
            print( str(e) )
            print('\n*************************************')
            print(  '*** Unable to open Nano IO device ***')
            print(  '***  Make sure it is plugged in   ***')
            print(  '***  and that no app is using it  ***')
            print(  '*************************************')
            print(  '***          Giving up            ***')
            print('*************************************\n')
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
         (sock.rig_type=='Hamlib' and sock.rig_type2=='IC9700') or \
         (sock.rig_type=='FLRIG'  and sock.rig_type2=='IC9700'):

        if P.PRACTICE_MODE:
            ser=serial_dummy()
    
        elif sock.rig_type2=='IC9700':
            # If direct connect, could use USB A ...
            #ser = P.sock.s
            # but, in general, we'll use USB B in case we are using hamlib for rig control
            print('OPEN KEYING PORT:',SERIAL_PORT10,BAUD)
            try:
                ser = serial.Serial(SERIAL_PORT10,BAUD,
                                    timeout=0.1,dsrdtr=0,rtscts=0)
                print('OPEN KEYING PORT: Sock Init...')
                sock.init_keyer()
                time.sleep(.1)
                ser.setDTR(False)
                ser.setRTS(False)  
                time.sleep(1)
                ser.setDTR(False)
                ser.setRTS(False)  
            except Exception as e: 
                print( str(e) )
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
                ser = serial.Serial(SERIAL_PORT4,BAUD,timeout=0.1,dsrdtr=0,rtscts=0)
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
                ser = serial.Serial(SERIAL_PORT2,BAUD,timeout=0.1)
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

        
