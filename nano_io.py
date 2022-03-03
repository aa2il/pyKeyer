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

NANO_BAUD=38400
#NANO_BAUD=19200

############################################################################################

# Read responses from the nano IO
def nano_read(ser,echo=False):
    txt=''
    while ser and ser.in_waiting>0:
        try:
            txt = ser.read(256).decode("utf-8")
        except:
            txt=''
        if echo:
            print('Nano:',txt)
    return txt

# Send chars/commands to the nano IO
def nano_write(ser,txt):
    # Need to make sure serial buffer doesn't over run - h/w/ flow control doesn't seem to work
    if ser:
        if ser.out_waiting>10:
            print('WAITING ....')
            while ser.out_waiting>0:
                time.sleep(1)
        cnt=ser.write(bytes(txt, 'utf-8'))

# Key down/key up for tuning
# This isn't working - need to explore when updating nanoIO code
def nano_tune(ser,tune):
    if tune:
        # Key down
        txt='~T'
    else:
        # Cancel - see nanoIO.ino for this little gem
        txt=']'
    print('NANO_TUNE:',txt)
    if ser:
        ser.write(bytes(txt, 'utf-8'))

# Open up comms to nano IO
def open_nano(baud=NANO_BAUD):

    # Open port
    ser = serial.Serial(SERIAL_NANO_IO,baud,timeout=0.1,dsrdtr=0,rtscts=0)
    #ser = serial.Serial(SERIAL_NANO_IO,baud,timeout=0.1,\
    #                    dsrdtr=True,rtscts=True)
 
    # Wait for nano to wake up
    print('Waiting for Nano IO to start-up ...')
    ntries=0
    while ser.in_waiting==0 and ntries<100:
        ntries += 1
        time.sleep(.1)
    nano_read(ser)

    #nano_write(ser,"Test")
    #sys.exit(0)
    return ser

# Command nano to change WPM
def nano_set_wpm(ser,wpm,idev=1):

    if idev==1 or idev==3:
        # Set wpm of chars sent from the keyboard
        txt='~S'+str(wpm).zfill(3)+'s'
        nano_write(ser,txt)
            
    if idev==2 or idev==3:
        # Set wpm for the paddles
        txt='~U'+str(wpm).zfill(3)+'u'
        nano_write(ser,txt)
            
