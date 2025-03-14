############################################################################################
#
# nano_io.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
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
#
# For NANO_IO:
#
# Use ~~ to view list of keyer command, ~? to see current settings ...
# ~     Show cmds
# C,c   CW
# F,f   FSK
# T,t   Tune
# Svvvs Computer wpm
# Uvvvu Paddle wpm
# Dvvvd dash/dot ratio
# X0    ptt ON
# X1    ptt OFF
# X?    ptt state
# In    incr
# A,a   IambicA
# B,b   IambicB
# K,k   Straight
# 0     mark HIGH
# 1     mark LOW
# 4     45.45 baud
# 5     50 baud
# 7     75 baud
# 9     100 baud
# ?     Show config
# W     Write EEPROM
#
############################################################################################
#
# For K3NG_IO, CLI commands:
# \#		: Play memory # x
# \A		: Iambic A
# \B		: Iambic B
# \C		: Single paddle
# \D		: Ultimatic
# \E####	: Set serial number to ####
# \F####	: Set sidetone to #### hz
# \G		: Switch to bug mode
# \I		: TX line disable/enable
# \J###		: Set dah to dit ratio
# \L##		: Set weighting (50 = normal)
# \N		: Toggle paddle reverse
# \O		: Toggle sidetone on/off
# \Px<string>	: Program memory #x with <string>
# \Q#[#]	: Switch to QRSS mode with ## second dit length
# \R		: Switch to regular speed (wpm) mode
# \S		: Status report
# \T		: Tune mode
# \U		: PTT toggle
# \W#[#][#]	: Change WPM to ###
# \X#		: Swith to transmitter #
# \Y#		: Change wordspace to #
# \+		: Create prosign
# \!##		: Repeat play memoy
# \|####	: Set memory repeat (milliseconds)
# \*		: Toggle paddle echo
# \`		: Toggle straight key echo
# \^		: Toggle wait for carriage return to send CW / send C immediately
# \.		: Toggle dit buffer on/off
# \-		: Toggle dah buffer on/off
# \~		: Reset unit
# \:		: Toggle cw send echo
# \>		: Send serial number, then increment
# \<		: Send current serial umber
# \(		: Send current serial number in cut numbers
# \)		: Send serial number with cut numbers, then increment
# \[		: Set quiet paddle interruption - 0 to 20 element lengths; 0 = off
# \]		: PTT disable/enable
# \@		: Mill Mode
# \\		: Empty keyboard send buffer
# \/		: Paginated help
#
############################################################################################

import sys
import serial
import time
from utilities import find_serial_device,list_all_serial_devices,show_hex,error_trap
if sys.platform == "linux" or sys.platform == "linux2":
    import termios

############################################################################################

#NANO_IO_VIDPID='1A86:7523'
NANO_BAUD=3*38400

############################################################################################

"""
#  stty -F /dev/ttyUSB0 -hupcl
#

import termios

path = '/dev/ttyACM0'

# Disable reset after hangup
with open(path) as f:
    attrs = termios.tcgetattr(f)
    attrs[2] = attrs[2] & ~termios.HUPCL
    termios.tcsetattr(f, termios.TCSAFLUSH, attrs)

ser = serial.Serial(path, 9600)

"""

# Function to disable/enable DTR hangup
def set_DTR_hangup(device,ENABLE=False):

    # Disable reset after hangup - should be done at system level already
    if sys.platform == "linux" or sys.platform == "linux2":
        with open(device) as f:
            attrs = termios.tcgetattr(f)
            if ENABLE:
                # If the keyer needs a full reset, enable the DTR hangup
                print('Turning on DTR hangup ...')
                attrs[2] = attrs[2] | termios.HUPCL
            else:
                # Normally, everything is fine so disable DTR Hangup
                print('Turning off DTR hangup ...')
                attrs[2] = attrs[2] & ~termios.HUPCL
            termios.tcsetattr(f, termios.TCSAFLUSH, attrs)



# Interface to keying device
class KEYING_DEVICE():
    def __init__(self,P,device,protocol,baud=NANO_BAUD):

        # Init
        #self.winkey_mode=0x15                        # Iambic A + no paddle echo + serial echo + contest spacing
        #self.winkey_mode=0x55                        # Iambic A + paddle echo + serial echo + contest spacing
        self.winkey_mode=0x51                        # Iambic A + paddle echo + contest spacing
        self.ser = None

        # Find serial port to the device
        print("\nNANO_IO INIT: Opening keyer ... device=",device)
        if device:
            self.device=device
        else:
            KEYER_DEVICE_ID = P.SETTINGS["MY_KEYER_DEVICE_ID"]
            print('\tKEYER_DEVICE_ID =',KEYER_DEVICE_ID)
            
            print("NANO_IO INIT: Searching for nanoIO device ...")
            #self.device=find_serial_device('nanoIO',0,1)
            self.device,self.vid_pid=find_serial_device(KEYER_DEVICE_ID,0,1)
            if not self.device:
                print("NANO_IO INIT: Couldn't find nanoIO device - trying nanIO32 ...")
                self.device=find_serial_device('nanoIO32',0,1)
                if not self.device:
                    print("NANO_IO INIT: Couldn't find nanoIO32 device - giving up!")
                    sys.exit(0)

        # Disable reset after hangup - should be done at system level already
        set_DTR_hangup(self.device,False)

        # Open serial port to the device
        print('Opening serial port ...')
        print('\tdevice=',self.device,'\tbaud=',baud)
        self.ser = serial.Serial(self.device,baud,timeout=0.1,
                                 dsrdtr=True,rtscts=0)
        #                                 dsrdtr=False,rtscts=0)
            
        self.protocol=protocol
        #time.sleep(.1)
        #self.ser.reset_input_buffer
        #self.ser.reset_output_buffer
        #time.sleep(.1)
 
        # Make sure its in CW & Iambic-A mode & show current settings
        print('Initial setup ...')
        if self.protocol=='NANO_IO':
            self.delim='~'
            self.wait4it(.1,.1,10)
            self.send_command('C')
            self.send_command('A')
            self.send_command('?')
        elif self.protocol=='K3NG_IO':
            self.delim='\\'
            self.wait4it(2,.1,10)
            self.send_command('R')          # Regular speed mode
            self.send_command('A')          # Iambic A
            self.send_command('Y5')         # Contest word spacing
            self.send_command('S')          # Show status
        elif self.protocol=='WINKEYER':
            self.delim=''
            ntries = self.wait4it(0,.1,10)
            print('Found it after',ntries,'tries')
            #self.send_command(chr(0)+chr(2))          # Open
            #time.sleep(1)
            #self.send_command(chr(2)+chr(20))          # 20 wpm
            #time.sleep(1)
            #self.send_command(chr(16+5))               # Get status byte - Doesn't seem to work
            #time.sleep(1)
            #self.send_command(chr(0)+chr(9))          # Get FW major version - not in WK2
            #time.sleep(1)
            #self.send_command(chr(0)+chr(12))          # Dump eprom
            #time.sleep(1)
            #self.send_command('test')                   # Test Msg - make sure we can send lower case text!
            #self.send_command('TEST')                   # Test Msg

            self.send_command(chr(0x0E)+chr(self.winkey_mode))       
            time.sleep(1)
            
        else:
            print('KEYER_DEVICE INIT: Unknown device protocol:',protocol)
            sys.exit(0)

        # Let's see what we've got so far
        time.sleep(1)
        txt=self.nano_read()
        print('KEYING DEVICE INIT: txt=',txt,len(txt))
        if self.protocol=='WINKEYER':
            print(show_hex(txt))
        print('')
        #sys.exit(0)
        

    # Wait for the device to wake-up
    def wait4it(self,t1,t2,n):

        # Wait for nano to wake up
        print('Waiting for Nano IO to start-up ...')
        time.sleep(t1)
        ntries=0
        while self.ser.in_waiting==0 and ntries<n:
            ntries += 1
            print('\tWAIT4IT: attempt',ntries,' of',n,' ...')
            if self.protocol=='NANO_IO':

                # Check for proper device by issuing status query and looking for proper response:
                self.send_command('?')
                time.sleep(t2)
                txt=self.nano_read()
                print(ntries,txt)
                if 'nanoIO ver' in txt:
                    print('WAIT4IT: Found NANO_IO keying device - yippee!')
                    break
                
            elif self.protocol=='K3NG_IO':

                # Check for proper device by issuing status query and looking for proper response:
                self.send_command('?')
                time.sleep(t2)
                txt=self.nano_read()
                print(ntries,txt)
                if 'K3NG Keyer' in txt:
                    print('WAIT4IT: Found NANO_IO keying device - yippee!')
                    break
                
            elif self.protocol=='WINKEYER':

                # First, we need to open the device
                self.send_command(chr(0)+chr(2))
                time.sleep(t2)
                if self.ser.in_waiting:
                    print('WAIT4IT: WINKEYER appears to be opened ...')

                    # Send 'ABC' and see if it gets echoed back
                    self.send_command(chr(0)+chr(4)+'A')  # Echo test
                    self.send_command(chr(0)+chr(4)+'B')  # Echo test
                    self.send_command(chr(0)+chr(4)+'C')  # Echo test
                    time.sleep(t2)
                    txt=self.nano_read()
                    print(ntries,txt,'\t',show_hex(txt))
                    #if txt==chr(0x17)+'ABC':
                    if chr(0x17) in txt and 'ABC' in txt:
                        print('WAIT4IT: Found WINKEYER keying device - yippee!')
                        break
                
            else:

                print('WAIT4IT: ERROR - no test specified for UNKNOWN KEYER!!!')
                time.sleep(t2)
                sys.exit(0)
                
        else:
            print('NANO_io->WAIT4IT: Could not find keyer device - giving up!!!')
            sys.exit(0)
        return ntries

    # Send a command to the nano 
    def send_command(self,txt):
        try:
            self.nano_write(self.delim+txt)
        except: 
            error_trap('SEND NANO COMMAND: Problem with write - giving up')

    # Read responses from the nano IO
    def nano_read(self,echo=False):
        txt=''
        while self.ser and self.ser.in_waiting>0:
            try:
                if True:
                    txt1 = self.ser.read(256).decode("utf-8",'ignore')
                    txt += txt1
                else:
                    # Winkeyer returns some funny combos
                    # It looks like it sends some flow control chars
                    # in the form of 0xc2 and 0xc6.  These appear to be
                    # use to keep the computer from trying to send something
                    # while the paddles are engaged.  We aren't that
                    # sophisticated so it probablt safe to ignore these for now.
                    txt1 = self.ser.read(256)
                    txt = txt + txt1.decode("utf-8",'ignore')
                    print('NANO READ ECHO:',txt1,'\t',len(txt1),
                          '\n',show_hex(txt1),
                          '\n',txt,'\t',show_hex(txt),'\t',len(txt))
            except:
                error_trap('NANO READ ECHO ERROR')
                
        if echo:
            print('NANO READ ECHO:',txt,'\t',show_hex(txt))
        return txt

    # Send chars/commands to the nano IO
    def nano_write(self,txt):
        # Need to make sure serial buffer doesn't over run - h/w flow control doesn't seem to work
        if self.ser:
            if self.ser.out_waiting>10:
                print('WAITING ....')
                while self.ser.out_waiting>0:
                    time.sleep(1)
            cnt=self.ser.write(bytes(txt,'utf-8'))
            #print('NANO WRITE: txt=',txt,'\n',show_hex(txt),'\tcnt=',cnt)

            #time.sleep(1)
            #txt2=self.nano_read(echo=True)

    # Change WPM
    def set_wpm(self,wpm,idev=1):

        DEBUG=False

        if DEBUG:
            print('NANO_IO: SET WPM: wpm=',wpm,'\tidev=',idev,'\tprot=',self.protocol)
        
        if idev==1 or idev==3:
            # Set wpm of chars sent from the keyboard
            if self.protocol=='NANO_IO':
                txt='S'+str(wpm).zfill(3)+'s'
            elif self.protocol=='K3NG_IO':
                txt='W'+str(wpm)+chr(13)
            elif self.protocol=='WINKEYER':
                txt=chr(2)+chr(wpm)
            else:
                txt=None
            if DEBUG:
                print('NANO SET WPM1: txt=',txt,'\t',show_hex(txt))
            if txt:
                self.send_command(txt)
            
        if idev==2 or idev==3:
            # Set wpm for the paddles
            if self.protocol=='NANO_IO':
                txt='U'+str(wpm).zfill(3)+'u'
            elif self.protocol=='K3NG_IO':
                txt='w'+str(wpm)+chr(13)
            elif self.protocol=='WINKEYER':
                txt=chr(2)+chr(wpm+64)
            else:
                txt=None
            if DEBUG:
                print('NANO SET WPM2: txt=',txt,'\n',show_hex(txt))
            if txt:
                self.send_command(txt)
                
        #sys.exit(0)

    # Key down/key up for tuning
    # This isn't working - need to explore when updating nanoIO code
    def tune(self,tune):
        if tune:
            # Key down
            if self.protocol=='NANO_IO':
                txt='~T'
            elif self.protocol=='K3NG_IO':
                txt='\T'
            elif self.protocol=='WINKEYER':
                txt=chr(0x0B)+chr(0x01)
            else:
                txt=None
        else:
            # Cancel 
            if self.protocol=='NANO_IO':
                txt=']'     # See nanoIO.ino for this little gem
            elif self.protocol=='K3NG_IO':
                txt='\T'    # Havent tested this
            elif self.protocol=='WINKEYER':
                txt=chr(0x0B)+chr(0x00)
            else:
                txt=None
        print('NANO_TUNE:',txt)
        #if ser:
        self.ser.write(bytes(txt,'utf-8'))

            
    # Immediate abort
    def abort(self):
        
        if self.protocol=='NANO_IO':
            self.nano_write('\\')
        elif self.protocol=='K3NG_IO':
            self.nano_write('\\')
        elif self.protocol=='WINKEYER':
            self.send_command(chr(0x0A))             # Clear buffer should do the trick
                              
    #
    def close(self):
        if self.ser:
            print('KEYING DEVICE CLOSED.')
            self.ser.close()
