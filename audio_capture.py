############################################################################################
#
# audio_capture.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Functions related audio capturing.
#
# To Do - does the standalone version of this still work and under python 3?
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
import time
from audio_io import WaveRecorder

############################################################################################

class AUDIO_CAPTURE():
    def __init__(self,P):

        print('AUDIO_CAPTURE: Init ...')
        self.started = False
        self.enabled = False
        P.rec=None
        self.P = P
        self.nout=0
        self.nblocks=0

        #P.CAPTURE = True
        print('CAPTURE AUDIO: Preparing wave recorder for rig audio capture ...')

        s=time.strftime("_%Y%m%d_%H%M%S", time.gmtime())      # UTC
        dirname=''
        P.wave_file = dirname+'capture'+s+'.wav'
        print('\nOpening',P.wave_file,'...')

        # Seems like gain may depend on system audio setting
        # Need to make this adaptive???
        if P.sock.rig_type2=='FT991a':
            gain=[2,1]            # was 4
        elif P.sock.rig_type2=='FTdx3000':
            gain=[1,1]
        else:
            gain=[1,1]
            
        WAVE_RATE=8000
        nchan=1
        P.rec = WaveRecorder(P.wave_file, 'wb',
                             channels=nchan,
                             wav_rate=WAVE_RATE,
                             GAIN=gain)

        # Check for sound card
        P.RIG_AUDIO_IDX = None
        if P.sock.rig_type2=='FTdx3000':
            P.AUDIO_DEVICE  = 'USB Audio Device'           # External sound card
            P.RIG_AUDIO_IDX = self.P.rec.list_input_devices(self.P.AUDIO_DEVICE)
            card='External'
        if P.RIG_AUDIO_IDX==None:
            P.AUDIO_DEVICE  = 'USB Audio CODEC'            # Rig sound card
            P.RIG_AUDIO_IDX = self.P.rec.list_input_devices(self.P.AUDIO_DEVICE)
            card='Rig'
            P.SIDETONE=True
        if P.RIG_AUDIO_IDX==None:
            print('\nAUDIO CAPTURE - Cant find sound card!!!')
            sys.exit(0)
        print('AUDIO CAPTURE: Using ',card,' Soundcard \tRIG AUDIO IDX=',P.RIG_AUDIO_IDX)
        
    def start(self):
        print('CAPTURE Starting ...',self.P.RIG_AUDIO_IDX)
        self.P.rec.start_recording(self.P.RIG_AUDIO_IDX)
        self.started = True
        self.enabled = True
        
    # Main routine that starts audio capture
    def run(self):
        print('AUDIO_CAPTURE Exec Starting ...')
        P=self.P

        # Loop until exit event is set
        while not P.Stopper.isSet():

            if P.rec:
                rb=P.rec.rb
                nsamps=rb.nsamps
                if nsamps>1024:
                    n=nsamps-1024                    
                    data=rb.pull(n)
                    P.rec.write_data(data)               # Save to disk also
                    self.nout+=n
                    if self.nblocks<100:
                        self.nblocks+=1
                    else:
                        #print('AUDIO_CAPTURE: Wrote ',self.nout,' samples so far ...')
                        self.nblocks=0
            time.sleep(0.1)
                
        print('CAPTURE Exec Done.')

    def pause(self):
        self.P.rec.stop_recording()
        self.enabled = False

    def resume(self):
        self.P.rec.resume_recording()
        self.enabled = True

