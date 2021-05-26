############################################################################################

# Nano IO - J.B.Attili - 2021

# Functions related to the nano IO interface

############################################################################################

import sys
import serial
from rig_io.ft_tables import SERIAL_NANO_IO
import time

############################################################################################

def nano_read(ser,echo=True):
    while ser.in_waiting>0:
        txt = ser.read(256).decode("utf-8")
        if echo:
            print('Nano:',txt)
    return txt

def nano_write(ser,txt):
    ser.write(bytes(txt, 'utf-8'))

def open_nano(baud=28400):

    # Open port
    if True:
        ser = serial.Serial(SERIAL_NANO_IO,baud,timeout=0.1,dsrdtr=0,rtscts=0)
    else:
        # Try to open port without reset - no luck yet
        #ser = serial.serial_for_url(port, 
        ser = serial.serial_for_url(SERIAL_NANO_IO,
                                    baud,
                                    do_not_open=True)
        #timeout=0.1,
        #dsrdtr=False,
        #new_serial.applySettingsDict(settings)
        #ser.rts = False
        ser.dtr = False
        ser.open()
        #    new_serial.break_condition = self.serial.break_condition
 
    # Wait for nano to wwake up
    print('Waiting for Nano IO to start-up ...')
    while ser.in_waiting==0:
        time.sleep(.1)
    nano_read(ser)

    #nano_write(ser,"Test")
    #sys.exit(0)
    return ser
            
def nano_set_wpm(ser,wpm):
    txt='~S'+str(wpm).zfill(3)+'s'
    #print('txt=',txt)
    nano_write(ser,txt)
            
    txt='~U'+str(wpm).zfill(3)+'u'
    #print('txt=',txt)
    nano_write(ser,txt)
            
