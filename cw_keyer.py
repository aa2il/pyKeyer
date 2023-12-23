############################################################################################
#
# cw_keyer.py - Rev 1.0
# Copyright (C) 2021-3 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for translating keyboard strokes into CW chars.  The rig can be keyed
# via the DTR line or, more reliably, via a nanoIO ardunino-based interface.
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

import time
import socket
import threading
import sys
import serial

############################################################################################

TEST_MODE = True
TEST_MODE = False

MIN_WPM=5
MAX_WPM=50

############################################################################################

# Table of Morse code elements
#morse=["" for i in range(128)]
morse=128*[""]
morse[32]=" ";

# Numbers
morse[48]="-----"; # 0
morse[49]=".----";
morse[50]="..---";
morse[51]="...--";
morse[52]="....-";
morse[53]=".....";
morse[54]="-....";
morse[55]="--...";
morse[56]="---..";
morse[57]="----."; # 9

# Punc
morse[33]="-.-.--";   # !
morse[34]="";         # "     0b01010010
morse[35]="";         # #     0b00000001
morse[36]="...-..-";  # $     0b11001000
morse[39]=".----.";   # '     0b01011110
morse[40]="-.--.";    # (     0b00101101
morse[41]="-.--.-";   # )     0b01101101
morse[44]="--..--";   # ,
morse[46]=".-.-.-";   # .
morse[47]="-..-.";    # /
morse[58]="---...";   # :
morse[59]="-.-.-.";   # :
morse[63]="..--..";   # ?
morse[64]=".--.-.";   # @
morse[92]=".-..-.";   # \

# Letters
morse[65]=".-";     # A
morse[66]="-...";
morse[67]="-.-.";
morse[68]="-..";
morse[69]=".";
morse[70]="..-.";   # F
morse[71]="--.";
morse[72]="....";
morse[73]="..";
morse[74]=".---";
morse[75]="-.-";     # K
morse[76]=".-..";
morse[77]="--";      # M
morse[78]="-.";
morse[79]="---";
morse[80]=".--.";
morse[81]="--.-";
morse[82]=".-.";
morse[83]="...";
morse[84]="-";
morse[85]="..-";
morse[86]="...-";
morse[87]=".--";
morse[88]="-..-";
morse[89]="-.--";    # Y
morse[90]="--..";

# Prosigns - This matches what is the nano IO uses
morse[37]="...-.-";    # % = <SK>	0b01101000
morse[38]=".-...";     # & = <AS>	0b00011010
morse[42]="";          # * 	        0b00000001
morse[43]="-.--.";     # + = <KN>	0b00101101
morse[45]="-....-";    # - = <BT>	0b00110001
morse[60]=".-...";     # < = <AS>	0b00100010
morse[61]="-...-";     # = = <BT>	0b00110001
morse[62]=".-.-.";     # > = <AR>	0b00101010

############################################################################################

# The key object - this is where all the hard work is really done
class Keyer():

    def __init__(self,P,DEFAULT_WPM=25,KEY_DOWN=False):

        self.P = P
        if DEFAULT_WPM<5:
            self.DEFAULT_WPM=25
        else:
            self.DEFAULT_WPM=DEFAULT_WPM
        self.KEY_DOWN = KEY_DOWN

        # Set defaults
        self.WPM      = self.DEFAULT_WPM
        self.dotlen   = 1.2/self.WPM 
        self.time=time.time();
        self.enable = True
        self.stop   = False
        self.Udp=False
        self.Cmd=[]

        # Compute weight (in dots) of each char
        self.weight=128*[0]
        for i in range(128):
            for el in morse[i]:
                if el in [' ','-']:
                    self.weight[i]+=3
                else:
                    self.weight[i]+=1
                self.weight[i]+=1
                

    def abort(self):
        print('CW_KEYER - ABORT!')
        self.evt.clear()
        self.stop=True
        if self.P.USE_KEYER:
            #self.P.keyer_device.nano_write('\\')
            self.P.keyer_device.abort()
            return

    # Routine to send a message in cw by toggling DTR line
    #    1. The length of a dot is 1 time unit.
    #    2. A dash is 3 time units.
    #    3. The space between symbols (dots and dashes) of the same letter is 1 time unit.
    #    4. The space between letters is 3 time units.
    #    5. The space between words is 7 time units.
    def send_cw(self,msg):

        # Init
        ser = self.P.ser
        WPM = self.WPM
        dotlen = self.dotlen

        # If using nano IO interface, send the char & let the nano do the rest
        if self.P.USE_KEYER:
            wght=0
            for char in msg.upper():
                wght+=self.weight[ord(char)]

            dt=dotlen*wght
            #print('send_cw: msg=',msg,'\t@ wpm=',self.WPM,'\twght=',wght,'\tdt=',dt)
            self.P.keyer_device.nano_write(msg)
            
            time.sleep(dt)
            return

        # If in practice mode, use pc audio instead
        elif self.P.PRACTICE_MODE:
            #print('KEYER->SEND_CW: msg=',msg,len(msg))
            self.sidetone.send_cw(msg,self.WPM,0,True)
            return

        elif TEST_MODE:
            # Disable for testing purposes
            print("send_cw:",msg)    # ,WPM,dotlen
            return

        # If we get here, we have to do all the heavy lifiting.
        # Loop over all chars in message to form symbols and timing
        for char in msg.upper():

            i=ord(char)
            cw=morse[i]
            dt=time.time() - self.time;
            print('SEND_CW: sending ',char,'\tdotlen=',dotlen)
            
            # Loop over all elements in this char
            startup = 0.02                            # Additional time needed to overcome OS limitations?
            if i>=32: #    or dt<3*dotlen ):
                for el in cw:
                    if( el==' ' ):
                        # After each char, 3 short spaces have already been added (see code below).
                        # Hence, we only need 4 more short spaces to get letter spacing correct (7 short).
                        # This seems too long so we cheat and only 3 short spaces (6 short)
                        #print('Key Up')
                        ser.setDTR(False)
                        time.sleep(3*dotlen + startup)
                    elif( el=='.' ):
                        # Enable DTR for dot period
                        #print('Key Down')
                        ser.setDTR(self.enable)
                        time.sleep(dotlen + startup)
                    elif( el=='-' ):
                        # Enable DTR for 3 dot periods
                        #print('Key Down')
                        ser.setDTR(self.enable)
                        time.sleep(3*dotlen + startup)

                    # After each element, we insert a short space to effect element spacing
                    #print('Key Up')
                    ser.setDTR(False)
                    time.sleep(dotlen - startup)
                    
                # Effect spacing between letters - we've already added one short space
                # so we only need 2 more to effect char spacing
                ser.setDTR(False)
                time.sleep(2*dotlen)
                self.time=time.time();

    # Set speed
    def set_wpm(self,wpm):
        ser = self.P.ser
        
        if wpm>0:
            print("SET_WPM: Setting speed to ",wpm)
            self.WPM = wpm
            self.dotlen=1.2/self.WPM

            if self.P.USE_KEYER:
                print("SET_WPM: Setting NANO speed to ",wpm)
                if self.P.LOCK_SPEED:  
                    self.P.keyer_device.set_wpm(wpm,idev=3)
                    self.P.gui.PaddlingWin.WPM_TXT.set(str(wpm))
                else:
                    self.P.keyer_device.set_wpm(wpm)
                self.P.gui.WPM_TXT.set(str(wpm))

    def txt2morse(self,msg):
        print('\nTXT2MORSE: msg=',msg)
        tdown=0
        times=[]
        dotlen_ms = int(1000*self.dotlen)

        for char in msg.upper():
            i=ord(char)
            if i>32 and i<128:
                cw=morse[i]
                for el in cw:
                    times.append(tdown)
                    if( el=='.' ):
                        tdown+=2*dotlen_ms            # Element plus space between elements
                    elif( el=='-' ):
                        tdown+=4*dotlen_ms

                tdown+=2*dotlen_ms                    # Space between letters = 3 dits

            else:
                tdown+=4*dotlen_ms                    # Space between letters = 7 dits

        #print('IDEAL TIMING:',times,'\n')
              
                    
    # Get speed
    def get_wpm(self):
        return self.WPM

    # Enable & disable TX keying
    def enable(self):
        self.enable = True

    def disable(self):
        self.enable = False

    # This was the guts of cw_server - need to make more efficent but works for now
    # Former UDP Commands for client/sever model:
    #        [RESET]   Reset to defaults
    #        [EXIT]    Exit server
    #        [WPM##]   Set WPM to ##
    #        [+#]      Increase WPM by # 
    #        [-#]      Decrease WPM by # 
    #        [TUNE##]  Key TX for ## sec.
    #        []
    def send_msg(self,msg):

        print('SEND_MSG: ',msg,' at ',self.WPM,' wpm - evt=',self.evt.isSet())
        P=self.P
        ser = self.P.ser

        # Testing only
        if self.P.USE_KEYER and ('[' not in msg) and (']' not in msg) and True:
            print('send_msg: msg=',msg,'\t@ wpm=',self.WPM)
            self.P.keyer_device.nano_write(msg)
            self.evt.set()           # Signal to other processes that we've went the message
            return
        
        self.stop   = False
        txt2=''
        for ch in msg:
            #print('ch=',ch)

            self.stop = self.stop or P.Stopper.isSet()
            if self.stop:
                self.stop   = False
                print('SEND_MSG: Aborting msg ...')
                break
            
            # Check for any UDP commands - they are encapsolated by []
            if ch=='[':
                # Start of a Udp command
                self.Udp=True
                self.Cmd=[]

            elif ch==']':
                # End of a Udp command
                self.Udp=False
                cmd2=''.join(self.Cmd)
                cmd2=cmd2.upper()
                print("cmd2=",cmd2)   # ,'\t',cmd2[:4])

                # Execute the command
                if cmd2[0]=='~':
                    # Direct command for the nano io
                    cmd2=''.join(self.Cmd)
                    print('Nano Cmd:',cmd2)
                    self.send_cw(''.join(self.Cmd))

                    # Allow the response to be echoed in process_chars
                    P.NANO_ECHO=True

                elif cmd2=="RESET":
                    # Reset defaults & reopen comm port
                    print("Reseting WPM to ",self.DEFAULT_WPM," wpm ...")
                    self.set_wpm(self.DEFAULT_WPM)

                    print("Reseting serial port ...")
                    self.P.ser = serial.Serial(ser.PORT,ser.BAUD,timeout=0.1)
                    self.P.ser.setDTR(False)

                #elif cmd2=="EXIT":
                    # Exit server
                    #print "Exiting server ..."
                    #sys.exit(0)

                elif cmd2[:3]=="WPM":
                    # Set speed
                    self.set_wpm( int(cmd2[3:]) )

                elif cmd2[:3]=="QSY":
                    # Change freq
                    df = float( cmd2[3:] )
                    frq = .001*self.P.sock.freq + df
                    print('DF=',df,self.P.sock.freq,frq)
                    self.P.sock.freq = self.P.sock.set_freq(frq)

                elif cmd2[:3]=="LOG":
                    # log the qso
                    print('SEND_MSG: Logging ...')
                    self.evt.set()
                    self.P.gui.log_qso()

                elif cmd2=="SERIAL":
                    # Substitute SERIAL NUMBER OUT
                    MY_CNTR=cut_numbers(P.MY_CNTR)
                    self.send_cw(MY_CNTR)
                    txt2+=MY_CNTR

                elif cmd2=="MYNAME":
                    # Substitute my name
                    self.send_cw(MY_NAME)
                    txt2+=MY_NAME

                elif cmd2=="MYSKCC":
                    # Substitute my skcc no.
                    self.send_cw(MY_SKCC)
                    txt2+=MY_SKCC

                elif cmd2=="MYQTH":
                    # Substitute my name
                    self.send_cw(MY_QTH)
                    txt2+=MY_QTH

                elif cmd2=="MYSEC":
                    # Substitute my name
                    self.send_cw(MY_SEC)
                    txt2+=MY_SEC

                elif cmd2=="MYCALL":
                    # Substitute my call
                    self.send_cw(MY_CALL)
                    txt2+=MY_CALL

                elif cmd2=="MYSTATE":
                    # Substitute my state
                    self.send_cw(MY_STATE)
                    txt2+=MY_STATE

                elif cmd2=="MYCOUNTY":
                    # Substitute my county
                    self.send_cw(MY_COUNTY)
                    txt2+=MY_COUNTY

                elif cmd2=="MYGRID":
                    # Substitute my state
                    self.send_cw(MY_GRID[0:4])
                    txt2+=MY_GRID[0:4]

                elif cmd2=="MYPREC":
                    # Substitute my precicence
                    self.send_cw(MY_PREC)
                    txt2+=MY_PREC

                elif cmd2=="MYCHECK":
                    # Substitute my check
                    self.send_cw(MY_CHECK)
                    txt2+=MY_CHECK

                elif cmd2=="MYCQZ":
                    # Substitute my check
                    self.send_cw(MYCQZ)
                    txt2+=MYCQZ

                elif cmd2=="CALL":
                    # Substitute his call
                    #print '@@@@@@@@@@@@@@@@@@@@@ CALL @@@@@@@@@@@@@@@@@@@@'
                    txt=self.P.gui.get_call()
                    #print txt
                    self.send_cw(txt)
                    txt2+=txt

                elif cmd2=="NAME":
                    # Substitute his name
                    #print '@@@@@@@@@@@@@@@@@@@@@ NAME @@@@@@@@@@@@@@@@@@@@'
                    txt=self.P.gui.get_name()
                    #print txt
                    self.send_cw(txt)
                    txt2+=txt

                elif cmd2=="RST":
                    # Substitute outgoing rst
                    #print '@@@@@@@@@@@@@@@@@@@@@ RST @@@@@@@@@@@@@@@@@@@@'
                    txt=self.P.gui.get_rst()
                    #print txt
                    self.send_cw(txt)
                    txt2+=txt

                elif cmd2[:4]=="TUNE":
                    # Key TX
                    #                print "Len=",len(cmd)
                    if len(cmd2)>4:
                        SEC=int(cmd2[4:])
                        print("Keying TX for ",SEC)
                        #pwr=read_tx_pwr(self)
                        self.P.sock.set_power(5)
                        if self.P.USE_KEYER:
                            self.P.keyer_device.tune(True)
                            time.sleep(SEC)
                            self.P.keyer_device.tune(False)
                        else:
                            ser.setDTR(True)
                            time.sleep(SEC)
                            ser.setDTR(False)
                        self.P.sock.set_power(99)
                    elif self.KEY_DOWN:
                        if self.P.USE_KEYER:
                            self.P.keyer_device.tune(False)
                        else:
                            ser.setDTR(False)
                        self.KEY_DOWN=False
                        print('TUNE - key up')
                        self.P.sock.set_power(99)
                    else:
                        #pwr=read_tx_pwr(self)
                        self.P.sock.set_power(5)
                        if self.P.USE_KEYER:
                            self.P.keyer_device.tune(True)
                        else:
                            ser.setDTR(True)
                        self.KEY_DOWN=True
                        print('TUNE - key down')

                elif cmd2[0]=="+":
                    # Increase speed
                    dWPM = int(cmd2[1:])
                    self.set_wpm( self.WPM + dWPM )
                    print("Increaing speed by",dWPM," to",self.WPM)

                elif cmd2[0]=="-":
                    # Decrease speed
                    dWPM = int(cmd2[1:])
                    self.set_wpm( self.WPM - dWPM )
                    print("Decreaing speed by",dWPM," to",self.WPM)

                else:
                    print("\n*** SEND_MSG: WARNING - Unknown command -",cmd2,'\n')
                    #sys.exit(1)

            else:
                if self.Udp:
                    # Collecting a command
                    self.Cmd.append(ch)

                else:
                    # Nothing special - key tranmitter
                    #print("Sending ",ch)
                    self.send_cw(""+ch)
                    txt2+=ch

        # Signal to other processes that we've went the message
        #print('SEND_MSG: Setting evt...')
        self.evt.set()
        return txt2


############################################################################################

# CW UDP server - runs in another thread
def cw_server(P,HOST='',PORT=7388):
    print('Starting cw server - ',HOST,PORT,'\n')
    keyer=P.keyer
    
    # Open udp socket
    try :
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)           # Need a timeout so we can interrupt/terminate it
        print('Socket created')
    except socket.error as msg :
        print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit(1)
 
    # Bind socket to local host and port
    try:
        s.bind((HOST, PORT))
        print('Socket bound',HOST,PORT)
    except socket.error as msg:
        print('CW_SERVER: Bind failed with Error Code ',msg[0],'-',msg[1])
        print(HOST,PORT)        
        sys.exit(1)

    # Keep talking with the client
    #while True:
    while not P.Stopper.isSet():

        # Receive data from client (data, addr)
        try:
            #print 'CW_SERVER ...'
            d = s.recvfrom(1024)
            data = d[0]
            addr = d[1]
     
            if data: 
                print('Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data)
                keyer.send_msg(data)
            else:
                print('CW_SERVER: blah - never should have got here!')
                sys.exit(1)

        except socket.error as msg:
            # print "msg=",msg
            pass

    print('CW_SERVER Done.')
    

    
# CW UDP server - old, depricated
class CW_Server_OLD(threading.Thread):
    
    def __init__(self,keyer,HOST='',PORT=7388):
        self.keyer=keyer
    
        print('Starting CW server - ',HOST,PORT)
    
        # Open udp socket
        try :
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s.settimeout(1)           # Need a timeout so we can interrupt/terminate it
            print('Socket created')
        except socket.error as msg :
            print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit(1)
 
        # Bind socket to local host and port
        try:
            self.s.bind((HOST, PORT))
            print('Socket bound')
        except socket.error as msg:
            print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit(1)

        # Start the server
        threading.Thread.__init__(self)
        self.start()                           # This apparently calls self.run ?!

    # The server listener runs in another thread
    def run(self):
        #print "Heydo!"
     
        # Keep talking with the client
        self.Done = False
        while not(self.Done):

            # Receive data from client (data, addr)
            try:
                d = self.s.recvfrom(1024)
                data = d[0]
                addr = d[1]
     
                if data: 
                    print('Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data)
                    self.keyer.send_msg(data)
                else:
                    print('CW_Server: blah - never should have got here!')
                    sys.exit(1)

            except socket.error as msg:
                # print "msg=",msg
                pass

        # That's all folks - terminate
        print("Server done.")
        #sys.exit(1)


