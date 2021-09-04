############################################################################################
#
# nano_io.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Functions related to the nano IO interface
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
import serial
from rig_io.ft_tables import SERIAL_NANO_IO
import time

############################################################################################

# Read responses from the nano IO
def nano_read(ser,echo=False):
    while ser.in_waiting>0:
        txt = ser.read(256).decode("utf-8")
        if echo:
            print('Nano:',txt)
    return txt

# Send chars/commands to the nano IO
def nano_write(ser,txt):
    ser.write(bytes(txt, 'utf-8'))

# Key down/key up for tuning
def nano_tune(ser,tune):
    if tune:
        # Key down
        txt='~T'
    else:
        # Cancel - see nanoIO.ino for this little gem
        txt=']'
    ser.write(bytes(txt, 'utf-8'))

# Open up comms to nano IO
def open_nano(baud=38400):

    # Open port
    ser = serial.Serial(SERIAL_NANO_IO,baud,timeout=0.1,dsrdtr=0,rtscts=0)
 
    # Wait for nano to wake up
    print('Waiting for Nano IO to start-up ...')
    while ser.in_waiting==0:
        time.sleep(.1)
    nano_read(ser)

    #nano_write(ser,"Test")
    #sys.exit(0)
    return ser

# Command nano to change WPM
def nano_set_wpm(ser,wpm):
    txt='~S'+str(wpm).zfill(3)+'s'
    #print('txt=',txt)
    nano_write(ser,txt)
            
    txt='~U'+str(wpm).zfill(3)+'u'
    #print('txt=',txt)
    nano_write(ser,txt)
            
