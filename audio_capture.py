############################################################################################
#
# capture.py - Rev 1.0
# Copyright (C) 2022-4 by Joseph B. Attili, aa2il AT arrl DOT net
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


    def start(self):
        print('CAPTURE Starting ...',self.P.RIG_AUDIO_IDX)
        if not self.P.RIG_AUDIO_IDX:
            self.CaptureAudioCB(-1)
            self.P.RIG_AUDIO_IDX = self.P.rec.list_input_devices('USB Audio CODEC')
        self.P.rec.start_recording(self.P.RIG_AUDIO_IDX)
        self.started = True
        self.enabled = True
        
    def pause(self):
        self.P.rec.stop_recording()
        self.enabled = False

    def resume(self):
        self.P.rec.resume_recording()
        self.enabled = True

    # Callback to toggle audio recording on & off
    def CaptureAudioCB(self,iopt=None):
        P=self.P
        print("\nCAPTURE AUDIO:  iopt=",iopt,'\tCAPTURE=',P.CAPTURE)
        if iopt==-1:
            iopt=None
            P.CAPTURE = not P.CAPTURE
            print("CAPTURE AUDIO:  Toggled P.CAPTURE",P.CAPTURE)
        if (iopt==None and not P.CAPTURE) or iopt==1:
            if not P.CAPTURE:
                #self.CaptureBtn['text']='Stop Capture'
                #self.CaptureBtn.configure(background='red',highlightbackground= 'red')
                P.CAPTURE = True
                print('CAPTURE AUDIO: Preparing wave recorder for rig audio capture ...')

                s=time.strftime("_%Y%m%d_%H%M%S", time.gmtime())      # UTC
                dirname=''
                P.wave_file = dirname+'capture'+s+'.wav'
                print('\nOpening',P.wave_file,'...')

                # Seems like this may depend on system audio setting
                # Need to make this adaptive???
                if P.sock.rig_type2=='FT991a':
                    gain=[4,1]
                elif P.sock.rig_type2=='FTdx3000':
                    gain=[1,1]
                else:
                    gain=[1,1]
                if P.osc:
                    rb22=P.osc.rb2
                else:
                    rb22=None
                WAVE_RATE=8000
                nchan=1
                P.rec = WaveRecorder(P.wave_file, 'wb',
                                     channels=nchan,
                                     wav_rate=WAVE_RATE,
                                     rb2=rb22,
                                     GAIN=gain)
                
        else:
            if P.CAPTURE:
                if P.RIG_AUDIO_IDX:
                    P.rec.stop_recording()
                    P.rec.close()
                    print('CAPTURE AUDIO : Wave recorder stopped ...')
                P.CAPTURE = False
                print('CAPTURE AUDIO : Capture rig audio stopped ...')

