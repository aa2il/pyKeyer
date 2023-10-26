#! /usr/bin/python3 -u
################################################################################
#
# WatchDog.py - Rev 1.0
# Copyright (C) 2021-3 by Joseph B. Attili, aa2il AT arrl DOT net
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
from utilities import freq2band
from tcp_server import open_udp_client,BANDMAP_UDP_PORT
from udp import UDP_msg_handler

################################################################################

VERBOSITY=0

################################################################################

# Function to monitor udp connections
def check_udp_clients(P):

    print('CHECK UDP CLIENTS:',P.UDP_SERVER,P.udp_client,P.udp_ntries)
    if True:
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

            """ 
            # Client to SDR - don't need this yet?

            Get rid of "self"s

            if not self.P.udp_client2:
                self.P.udp_ntries2+=1
                if self.P.udp_ntries2<=1000:
                    self.P.udp_client2=open_udp_client(self.P,SDR_UDP_PORT,
                                                       UDP_msg_handler,BUFFER_SIZE=32*1024)
                    if self.P.udp_client2:
                        print('WATCHDOG->CHECK UDP CLIENTS: Opened connection to BANDMAP.')
                        self.P.udp_ntries2=0
                        self.Last_BM_Check=time.time() - BANDMAP_UPDATE_INTERVAL+2     # Force first update in 2-seconds
                else:
                    print('Unable to open 2nd UDP client - too many attempts',self.P.udp_ntries2)
            """

        """
        # Query spot data to populate bandmap - SDR should take care of this for now
        if self.P.udp_client2:
            t = time.time()
            dt = t - self.P.Last_BM_Check
            band=self.P.BAND
            #print('WATCHDOG->CHECK_UDP_CLIENTS: t=',t,self.Last_BM_Check,
            #dt,'\tband=',band)
            if dt>BANDMAP_UPDATE_INTERVAL:
                msg='SpotList:'+band+':?\n'
                self.P.udp_client2.Send(msg)
                self.Last_BM_Check=t
                print('WATCHDOG->CHECK_UDP_CLIENTS: Spot List Query sent ..,',msg)
        """
   
def WatchDog(P):
    #print('Watch Dog ....')

    # Check if another thread shut down - this isn't complete yet
    if P.SHUTDOWN:
        if P.CAPTURE:
            P.rec.stop_recording()
            P.rec.close()
        if P.Timer:
            print('WatchDog - Cancelling timer ...')
            P.Timer.cancel()
        #P.gui.Quit()
        P.WATCHDOG = False
        P.Timer=None
        print('WatchDog - Shut down.')

    # Read radio status
    if P.sock.connection!='NONE':
        print('Watch Dog - reading radio status ...', P.sock.connection)
        if False:
            socket_io.read_radio_status(P.sock)
            #print('\tWoof Woof:',P.sock.freq, P.sock.band, P.sock.mode, P.sock.wpm)
            
            P.gui.rig.band.set(P.sock.band)
            x=str(int(P.sock.freq*1e-3))+' KHz  '+str(P.sock.mode)
            P.gui.rig.status.set(x)
            P.gui.rig.frequency=P.sock.freq
            P.gui.rig.mode.set(P.sock.mode)
            #self.ant.set(ant)
            #print('\tWoof Woof 2:',x)

            if P.sock.mode=='FM':
                gui_tone = P.gui.rig.SB_PL_TXT.get()
                print('\tWoof Woof - PL tone=',P.sock.pl_tone,gui_tone)
                if P.sock.pl_tone==0:
                    tone='None'
                else:
                    tone=str(P.sock.pl_tone)
                if tone!=gui_tone:
                    #print('*** Tone Mismatch ***')
                    P.gui.rig.SB_PL_TXT.set(tone)

        else:
            freq = P.sock.get_freq()
            mode = P.sock.get_mode()
            band = freq2band(1e-6*freq)

            P.gui.rig.band.set(band)
            x=str(int(freq*1e-3))+' KHz  '+str(mode)
            P.gui.rig.status.set(x)
            P.gui.rig.frequency=freq
            P.gui.rig.mode.set(mode)

    # Let user adjust WPM from radio knob
    if VERBOSITY>0:
        print("WatchDog - Checking WPM ...")
    if False:
        wpm=P.sock.wpm
    else:
        wpm = P.sock.read_speed()
    if wpm!=P.WPM and wpm>0:
        print("WatchDog - Changing WPM to",wpm)
        P.keyer.set_wpm(wpm)
        P.gui.WPM_TXT.set(str(wpm))
        P.WPM = wpm

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
        P.Timer = threading.Timer(1.0, WatchDog, args=(P,))
        P.Timer.setDaemon(True)                       # This prevents timer thread from blocking shutdown
        P.Timer.start()
    else:
        P.Timer=None
        print('... Watch Dog quit')
        P.WATCHDOG = False
        
        
