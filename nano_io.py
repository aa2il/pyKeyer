############################################################################################
#
# nano_io.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Functions related to the nano IO interface
#
# To Do:
#     The paddle switch point option isn't working
#            - pawing throw .ino file, it looks like switch point (0x12) is NOT supported
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
#
# See winkeyer docs for commands for winkeyer
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
        self.P = P
        #self.winkey_mode=0x15                        # Iambic A + no paddle echo + serial echo + contest spacing
        #self.winkey_mode=0x55                        # Iambic A + paddle echo + serial echo + contest spacing
        self.winkey_mode=0x51                         # Iambic A + paddle echo + contest spacing
        self.winkey_switch_point=0x40                 # Paddle switch point - deafult is 50=one dit time
        self.farnsworth_wpm=5                         # Farnsworth wpm - set low to effectively disable on start-up
        self.ser = None
        self.protocol=protocol
        self.winkey_version=None
 
        # Find serial port to the device
        print("\nNANO_IO: KEYING DEVICE INIT: Opening keyer ... device=",device)
        if device:
            self.device=device
        else:
            KEYER_DEVICE_ID = P.SETTINGS["MY_KEYER_DEVICE_ID"]
            print('\tKEYER_DEVICE_ID =',KEYER_DEVICE_ID)
            if KEYER_DEVICE_ID=='':
                print('\n*** Fatal Error *** Need to set MY_KEYER_DEVICE_ID ',
                      'in ~/.keyerrc so we can find the keyer port :-(')
                #print('\nRun this command to find out what devices/ports are available:')
                #print('\n\tpython3 -m serial.tools.list_ports -v')
                print('\nThese are the USB devices available:')
                list_all_serial_devices(True)
                sys.exit(0)

            print("NANO_IO INIT: Searching for nanoIO device ...")
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
        print('NANO_IO: KEYING DEVICE INIT: Opening serial port ...')
        print('\tdevice=',self.device,'\tbaud=',baud)

        # On windows for some reason, need to open at 9600 baud to reset the device and then
        # open at the 1200 baud used by winkeyer - go figure?!
        #print('BURP!',sys.platform,P.PLATFORM)
        if P.PLATFORM == "Windows" and True:
            self.ser = serial.Serial(self.device,9600,timeout=0.1,
                                     dsrdtr=True,rtscts=0)
            time.sleep(2)
            txt=self.nano_read()
            print('txt=',show_hex(txt))
            self.ser.close()
            time.sleep(2)

        Done=False
        ntries=0
        while not Done:
            ntries+=1
            print('NANO_IO: Attempting to open serial port ...',ntries)
            self.ser = serial.Serial(self.device,baud,timeout=0.1,
                                     dsrdtr=True,rtscts=0)
        
            time.sleep(1)
            print('\tin_waiting=',self.ser.in_waiting)

            if True:
                self.ser.setDTR(False)
                time.sleep(1)
                self.ser.setDTR(True)
                time.sleep(1)
                self.ser.setDTR(False)
                time.sleep(1)

                self.ser.reset_input_buffer()
                time.sleep(1)
                self.ser.reset_output_buffer()
                time.sleep(1)

            if False:
                print('Fiddling ... in_waiting=',self.ser.in_waiting)
                self.ser.flush()
                time.sleep(1)
                self.ser.flushInput()
                time.sleep(1)
                self.ser.read_all()
                time.sleep(1)

                print('Faddling ... in_waiting=',self.ser.in_waiting)
                self.ser.close()
                time.sleep(1)
                self.ser = serial.Serial(self.device,baud,timeout=0.1,
                                     dsrdtr=True,rtscts=0)
                time.sleep(2)
                txt=self.ser.read_all()
                time.sleep(1)
                print('nread=',len(txt))
                print('Fumbling ... in_waiting=',self.ser.in_waiting)

            """
            Done2=False
            ntries2=0
            while not Done2:
                ntries2+=1
                txt=self.nano_read()
                print('txt=',show_hex(txt))
                Done2=len(txt)<=2 or ntries2>5
            """
            txt=self.nano_read()
            n=min(len(txt),10)
            print('txt=',show_hex(txt[:n]))

            if len(txt)>2 and ntries<5:
                self.ser.close()
            else:
                Done=True
            
        # Make sure its in CW & Iambic-A mode & show current settings
        print('Initial setup ...')
        if P.PLATFORM == "Windows":
            delay=1.
        else:
            delay=1.   #  0.2
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
            ntries = self.wait4it(0,delay,10)
            print('Found it after',ntries,'tries')
            #self.send_command(chr(0)+chr(2))            # Open
            #time.sleep(1)
            #self.send_command(chr(2)+chr(20))           # 20 wpm
            #time.sleep(1)
            #self.send_command(chr(16+2)+chr(40))        # 40% switch point
            #time.sleep(1)
            #self.send_command(chr(16+5))                # Get status byte - Doesn't seem to work
            #time.sleep(1)
            #self.send_command(chr(0)+chr(9))            # Get FW major version - not in WK2
            #time.sleep(1)
            #self.send_command(chr(0)+chr(12))           # Dump eprom
            #time.sleep(1)
            #self.send_command('test')                   # Test Msg - make sure we can send lower case text!
            #self.send_command('TEST')                   # Test Msg

            # Make sure we're in proper mode
            self.send_command(chr(0x0E)+chr(self.winkey_mode))
            #time.sleep(.1)
            #self.send_command(chr(12)+chr(self.farnsworth))         # 5 wpm Farnsworth - effectively disabled
            #time.sleep(.1)

            # Set paddle switch point - 50 is default (one dit time), faster ops like it shorter  - Not support by K3NG version
            #self.send_command(chr(0x12)+chr(self.winkey_switch_point))
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
        print('Waiting for Nano IO to start-up - PROTOCOL=', self.protocol,' ...')
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
                print('\t\t0x02: in_waiting=',self.ser.in_waiting)

                if self.ser.in_waiting:
                    print('\tWAIT4IT: WINKEYER appears to be opened ...')
                    txt=self.nano_read()
                    print('\t\t',ntries,'\t0x02:\ttxt=',txt,'\t',show_hex(txt),'\t(Revision Code)')
                    txt2=txt
                    self.winkey_version=ord(txt[-1])

                    """
                    # We can do this again if we want
                    self.send_command(chr(0)+chr(2))
                    time.sleep(t2)
                    txt=self.nano_read()
                    print('\t\t',ntries,'\t0x02:\ttxt=',txt,'\t',show_hex(txt),'\t(Revision Code)')
                    txt2+=txt
                    """

                    # Send a few characters and see if they get echoed back
                    test_str='JBA@#$'
                    for ch in test_str:
                        txt=self.get_response(chr(0)+chr(4)+ch,0.1)     # Echo test
                        print('\t\t',ntries,'\t0x04'+ch,':\ttxt=',txt,'\t',show_hex(txt),'\t(Echo)')
                        txt2+=txt

                    # There shouldn't be any residual but let's just check and see
                    time.sleep(.1)
                    txt2+=self.ser.read_all().decode("utf-8")
                    print('\t\ttxt2=',txt2,'\t',show_hex(txt2))

                    # Did we find the keyer?
                    #if chr(0x17) in txt2 and 'ABC' in txt2:
                    #if self.winkey_version>=10 and self.winkey_version<40 and test_str in txt2:
                    if test_str in txt2:
                        print('WAIT4IT: Found WINKEYER keying device - yippee!')
                        print('\tRevision Code=',self.winkey_version)
                        break
                    else:
                        print('WAIT4IT: Unexpected response from keyer :-(')
                        print('\t\tin_waiting=',self.ser.in_waiting)
                
            else:

                print('WAIT4IT: ERROR - no test specified for UNKNOWN KEYER!!!')
                time.sleep(t2)
                sys.exit(0)
                
        else:
            print('NANO_io->WAIT4IT: Could not find keyer device - giving up!!!')
            sys.exit(0)
        return ntries

    # Send a command to the nano and read the response
    def get_response(self,cmd,delay=0):
        self.send_command(cmd)
        time.sleep(.1)
        txt=self.nano_read()
        return txt
    
    # Send a command to the nano 
    def send_command(self,txt):
        try:
            self.nano_write(self.delim+txt)
        except KeyboardInterrupt:
            print('Keyboard Interrupt - giving up!')
            sys.exit(0)
        except: 
            error_trap('SEND NANO COMMAND: Problem with write - giving up')

    # Read responses from the nano IO
    def nano_read(self,echo=False,READ_ALL=False):
        txt=''
        while self.ser and self.ser.in_waiting>0:
            try:
                if not READ_ALL:
                    txt1 = self.ser.read(256).decode("utf-8",'ignore')
                    txt += txt1
                else:
                    # Winkeyer returns some funny combos
                    # It looks like it sends some flow control chars
                    # in the form of 0xc2 and 0xc6.  These appear to be
                    # use to keep the computer from trying to send something
                    # while the paddles are engaged.  We aren't that
                    # sophisticated so it probably safe to ignore these for now.
                    txt1 = self.ser.read_all()
                    txt = txt + txt1  # .decode("utf-8",'ignore')
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
            if False:
                #self.ser.flush()
                print('NANO WRITE: txt=',txt,'\n',show_hex(txt),'\tcnt=',cnt)

                time.sleep(1)
                txt2=self.nano_read(echo=True)

    # Change WPM
    def set_wpm(self,wpm,idev=1,farnsworth=None):

        DEBUG=False
        DEBUG=True

        if DEBUG:
            print('NANO_IO: SET WPM: wpm=',wpm,'\tidev=',idev,'\tprot=',self.protocol,'\tfarnsworth=',farnsworth)
        
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

        # Set Farnsworth speed also
        if farnsworth!=None:
            self.farnsworth_wpm=farnsworth
            if self.protocol=='WINKEYER' and True:
                self.send_command(chr(0x12)+chr(self.winkey_switch_point))      # Not supported in k3ng version of keyer
                txt=chr(0x0d)+chr(self.farnsworth_wpm)
                self.send_command(txt)
                if DEBUG:
                    print('NANO SET FARNS WPM: txt=',txt,'\n',show_hex(txt))
                
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
