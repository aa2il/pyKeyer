############################################################################################
#
# capture.py - Rev 1.0
# Copyright (C) 2022 by Joseph B. Attili, aa2il AT arrl DOT net
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

"""
        # Capture
        if False:
            col += 2
            self.CaptureBtn = Button(self.root, text='Capture',command=self.CaptureAudioCB ) 
            self.CaptureBtn.grid(row=row,column=col,sticky=E+W)
            tip = ToolTip(self.CaptureBtn, ' Capture Rig Audio ' )
            self.CaptureAudioCB(-1)
        
"""

class AUDIO_CAPTURE():
    def __init__(self,P):

        print('AUDIO_CAPTURE: Init ...')
        self.P = P

    # Main routine that starts audio capture
    def run(self):
        print('CAPTURE Exec Starting ...')
        self.CaptureAudioCB(-1)

        """
        # Loop until exit event is set
        while not self.P.Stopper.isSet():
            time.sleep(1)
                
        print('CAPTURE Exec Done.')
        """

    # Callback to toggle audio recording on & off
    def CaptureAudioCB(self,iopt=None):
        P=self.P
        print("============================================== Capture Audio ...",iopt,P.CAPTURE)
        if iopt==-1:
            iopt=None
            P.CAPTURE = not P.CAPTURE
        if (iopt==None and not P.CAPTURE) or iopt==1:
            if not P.CAPTURE:
                #self.CaptureBtn['text']='Stop Capture'
                #self.CaptureBtn.configure(background='red',highlightbackground= 'red')
                P.CAPTURE = True
                print('Capture rig audio started ...')

                s=time.strftime("_%Y%m%d_%H%M%S", time.gmtime())      # UTC
                dirname=''
                P.wave_file = dirname+'capture'+s+'.wav'
                print('\nOpening',P.wave_file,'...')

                if P.sock.rig_type2=='FT991a':
                    gain=[4,1]
                else:
                    gain=[1,1]
                if P.osc:
                    rb22=P.osc.rb2
                else:
                    rb22=None
                P.rec = WaveRecorder(P.wave_file, 'wb',
                                     channels=1,wav_rate=8000,
                                     rb2=rb22,
                                     GAIN=gain)
                
                if not P.RIG_AUDIO_IDX:
                    P.RIG_AUDIO_IDX = P.rec.list_input_devices('USB Audio CODEC')
                P.rec.start_recording(P.RIG_AUDIO_IDX)
                
        else:
            if P.CAPTURE:
                #self.CaptureBtn['text']='Capture'
                #self.CaptureBtn.configure(background='green',highlightbackground= 'green')
                if P.RIG_AUDIO_IDX:
                    P.rec.stop_recording()
                    P.rec.close()
                P.CAPTURE = False
                print('Capture rig audio stopped ...')

