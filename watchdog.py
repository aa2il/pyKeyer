################################################################################
#
# WatchDog.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Watchdog timer for pyKeyer.
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

import threading
from utilities import freq2band,error_trap,show_hex,show_ascii
from tcp_server import open_udp_client,BANDMAP_UDP_PORT
from udp import UDP_msg_handler
from rig_io import SetSubDial
from tkinter import END
import time

################################################################################

VERBOSITY=0

################################################################################

class WatchDog:
    def __init__(self,P,msec):
        print('Watch Dog Starting ....')

        self.P = P
        self.dt =.001*msec
        P.SHUTDOWN = False

        # Kick off watchdog monito
        P.Timer = threading.Timer(self.dt, self.Monitor)
        P.Timer.daemon=True                       # This prevents timer thread from blocking shutdown
        P.Timer.start()
        
    # Function to monitor udp connections
    def check_udp_clients(P):

        print('CHECK UDP CLIENTS:',P.UDP_SERVER,P.udp_client,P.udp_ntries)
        if P.UDP_SERVER != None:

            # Client to BANDMAP
            if not P.udp_client:
                P.udp_ntries+=1
                if P.udp_ntries<=1000:
                    P.udp_client=open_udp_client(P,BANDMAP_UDP_PORT,
                                                 UDP_msg_handler)
                    if P.udp_client:
                        print('CHECK UDP CLIENTS: Opened connection to BANDMAP - port=',
                              BANDMAP_UDP_PORT)
                        P.udp_ntries=0
                else:
                    print('CHECK UDP CLIENTS: Unable to open UDP client - too many attempts',
                          P.udp_ntries)

    def Monitor(self):
        P=self.P
    
        # Check if another thread shut down - this isn't complete yet
        if P.SHUTDOWN:
            if P.CAPTURE:
                P.rec.stop_recording()
                P.rec.close()
            if P.Timer:
                print('WatchDog - Cancelling timer ...')
                P.Timer.cancel()
            P.WATCHDOG = False
            P.Timer=None
            print('WatchDog - Shut down.')

        # Monitor memory usage
        if P.MEM:
            P.MEM.take_snapshot()
            
        # Check if we are transmitting
        if P.DIGI and P.sock_xml.tx_evt.is_set():
            print('Watch Dog - PTT is on ...', P.sock.connection)
            try:
                state=P.sock_xml.ptt(-1)
                print('state=',state)
            except:
                error_trap('WATCHDOG: Unable to retrieve PTT state',1)
            
        # Read radio status
        # NEED TO MOVE ANYTHING THAT MESSES WITH THE GUI TO gui.gui_updater!!!!!!!!!!!!!!
        if P.sock.connection!='NONE' and not P.sock.tx_evt.is_set():
            print('Watch Dog - reading radio status ...', P.sock.connection,flush=True)

            P.FREQ = P.sock.get_freq()
            P.MODE = P.sock.get_mode()
            P.BAND = freq2band(1e-6*P.FREQ)
            
            # Let user adjust WPM from radio knob
            if P.MODE in ['CW']:
                if VERBOSITY>0:
                    print("WatchDog - Checking WPM ...")
                wpm = P.sock.read_speed()
                if wpm!=P.WPM and wpm>0 and not P.keyer.busy():
                    print("WatchDog - Changing WPM to",wpm)
                    P.keyer.set_wpm(wpm)
                    P.WPM2 = wpm

            # Keep an eye on the small knob
            #if not (P.SO2V or P.SPLIT_VFOs):
            #if P.sock.rig_type=='FLRIG' and not (P.SO2V or P.SPLIT_VFOs):
            #    SetSubDial(P.gui,'CLAR')
            if P.SO2V or P.SPLIT_VFOs:
                print('WATCHDOG: Need to check subdial ...')
                P.gui.CHECK_DIAL = 2
            elif P.gui.CHECK_DIAL>0:
                print('WATCHDOG: Subdial checked ...')
                SetSubDial(P.gui,'CLAR')
                P.gui.CHECK_DIAL-=1

        # Save program state to disk
        #print("WatchDog - Dirty Dozen ...")
        if P.DIRTY:
            P.gui.SaveState()

        # Compute QSO Rate
        if VERBOSITY>0:
            print("WatchDog - QSO Rate ...")
        P.gui.qso_rate()

        # Send out heart beat message - Cmd:Source:Msg
        if P.UDP_SERVER and False:
            print('WATCHDOG - Broadcasting heart beat ...')
            P.udp_server.Broadcast('HeartBeat:Keyer:Thump Thump - kerr chunk')

        # Open clients to BANDMAP and SDR
        #check_udp_clients(P)

        # Check if anything is going on with FLDIGI
        if P.DIGI and not P.sock_xml.tx_evt.is_set():
            print('WATCHDOG - Checking RX buff ...')
            
            # Get any new decoded text from RX box and put it in the big text box
            try:
                txt=P.sock_xml.get_rx_buff()
            except:
                error_trap('WATCHDOG: Unable to get rx buffer',1)
                txt=''
            if len(txt)>0:
                print('txt=',txt,'\tlen=',len(txt))
                #print('\t',show_hex(txt))
                print('\t',show_ascii(txt))
                P.gui.txt.insert(END, txt)
                P.gui.txt.see(END)

                # Save to disk also
                P.gui.fp_txt.write('%s' % (txt) )
                P.gui.fp_txt.flush()
                
                P.gui.root.update_idletasks()
            
        # Read rotor position
        if P.sock_rotor.connection!='NONE' or False:
            gui2=P.gui.rotor_ctrl
            pos=P.sock_rotor.get_position()
            #print('pos:',pos)
            if pos[0]==None:
                pos[0]=gui2.azlcd1.get()             # Temp
            if pos[0]!=None:
                if pos[0]>180:
                    pos[0]-=360
                if pos[0]<-180:
                    pos[0]+=360
                gui2.azlcd1.set(pos[0])
                gui2.ellcd1.set(pos[1])
                gui2.nominalBearing()
    
        # Reset timer
        if VERBOSITY>0:
            print("WatchDog - Timer ...")
        if not P.gui.Done and not P.SHUTDOWN and not P.Stopper.isSet():
            if P.DIGI:
                dt=0.2
            else:
                dt=1.0
            P.Timer = threading.Timer(self.dt, self.Monitor)
            P.Timer.setDaemon(True)                       # This prevents timer thread from blocking shutdown
            P.Timer.start()
        else:
            P.Timer=None
            print('... Watch Dog quit')
            P.WATCHDOG = False
        
        
