#! /usr/bin/python
############################################################################################
#
# sidetone.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Sidetone oscillator for code practice
#
# To Do - does the standalone version work under python3?
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

import pyaudio
import numpy as np
from cw_keyer import morse
import sys
import time
import sig_proc as dsp

###################################################################

# Prototype
def SideToneCB(in_data, frame_count, time_info, status):
    global osc
    
    if n+frame_count>len(x):
        n=0
    data = x[n:(n+frame_count)].astype(np.float32).tostring()
    #data = x.astype(np.float32).tostring()
    n+=frame_count
    print('Callback ...',len(data),len(x),frame_count,n)
    return (data, pyaudio.paContinue)


class SIDETONE_OSC():
    def __init__(self,WPM,AMP,F0,FS):

        print("\nCreating code practice osc ...")
        self.enable=False
        self.AMP=AMP
        self.F0=F0
        self.FS=float(FS)

        # Use non-blocking audio player
        self.rb     = dsp.ring_buffer2('Audio0',32*1024)
        self.rb2    = dsp.ring_buffer2('Audio1',32*1024)
        self.player = dsp.AudioIO(None,int(self.FS),self.rb,None,'B',True)
        self.player.start_playback(0,False)

        # Open PyAudio stream - blocking
        if False:
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(format=pyaudio.paFloat32,
                                      channels=1,
                                      rate=FS,
                                      output=True)
            #                                  stream_callback=SideToneSB)

        # Generate sigs
        self.gen_elements(WPM)

    # Signal generation 
    def gen_elements(self,WPM):
        self.WPM=WPM

        dotlen=1.2/self.WPM
        Ndit = int( self.FS*dotlen + 0.5)
        tt = np.arange(3*Ndit) / self.FS
        self.dah = self.AMP*np.sin(2 * np.pi * self.F0 * tt)
        self.dit = self.dah[0:Ndit]
        #print('Gen elements:',dotlen,Ndit,len(self.dit))
        self.space = 0*self.dit
        self.long_space = 0*self.dah

        # Shape leading & trailing edges to avoid clicks
        Trise = 10e-3                   # Shape length
        Nrise = int( self.FS*Trise )
        t = np.arange(Nrise) / self.FS
        a = 0.5*(1. + np.cos(np.pi*t/Trise) )
        env1 = np.ones(Ndit)
        env1[0:Nrise]     = 1-a
        env1[-Nrise:Ndit] = a
        self.dit = env1 * self.dit
        
        env2 = np.ones(3*Ndit)
        env2[0:Nrise]     = 1-a
        env2[-Nrise:3*Ndit] = a
        self.dah = env2 * self.dah
        
        #print 'dit=',self.dit
        #print 'ev1=',env1
        
    # Routine to send a message in cw by sending tones to audio
    #    1. The length of a dot is 1 time unit.
    #    2. A dash is 3 time units.
    #    3. The space between symbols (dots and dashes) of the same letter is 1 time unit.
    #    4. The space between letters is 3 time units.
    #    5. The space between words is 7 time units.
    def send_cw(self,msg,WPM,AUDIO_ACTIVE):
        #print('SIDETONE->SEND_CW:  msg=',msg,len(msg))

        # Check for speed change
        if WPM != self.WPM:
            self.gen_elements(WPM)

        # Loop over all chars
        for char in msg.upper():

            i=ord(char)
            cw=morse[i]
            #print('SIDETONE->SEND_CW: Sending *',i,'*',char,'*',cw,'*')
            
            if i>=32:
                # Loop over all elements in this char
                for el in cw:
                    # After each element, we insert a short space to effect element spacing
                    if( el==' ' ):
                        # After each char, 3 short spaces have already been added (see code below).
                        # Hence, we need 4 short spaces to get letter spacing correct (7 short)
                        # This seems too long so we cheat and only 3 short spaces (6 short)
                        x = np.concatenate( (self.long_space,self.space) )
                    elif( el=='.' ):
                        x = np.concatenate( (self.dit,self.space) )
                    elif( el=='-' ):
                        x = np.concatenate( (self.dah,self.space) )

                    # Send the element
                    if AUDIO_ACTIVE:
                        self.rb.push(x)
                    self.rb2.push(x)

                # Effect spacing between letters - we've already added one short space
                # so we only need 2 more to effect char spacing
                x = np.concatenate( (self.space,self.space) )
                if AUDIO_ACTIVE:
                    self.rb.push(x)
                self.rb2.push(x)
                

    def play(self):
        x = np.concatenate( (self.dit,self.space,self.dah,self.space) )
        data = x.astype(np.float32).tostring()
        self.stream.write(data)

    def quit(self):
        # Close down
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


# If this file is called as main, run some test code
if __name__ == '__main__':
    print('Hey!')

    WPM=25
    AMP=0.5
    FS = 48000              # Playback rate
    F0 = 700
    osc = SIDETONE_OSC(WPM,AMP,F0,FS)
    
    osc.send_cw('Test',WPM)
    time.sleep(5)
    osc.send_cw('=',WPM)
    time.sleep(1)
    #osc.quit()
    
        
