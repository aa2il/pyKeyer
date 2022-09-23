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
import threading
if sys.version_info[0]==3:
    import queue
else:
    import Queue

###################################################################

# User params
FS = 8000    # 48000              # Playback rate
F1 = 680                # My pitch
F2 = 700                # Caller's pitch
AMP=0.5

################################################################################

def init_sidetone(P):
    
    if P.SIDETONE or True:
        print('Init SIDETONE ...')
        P.osc = SIDETONE_OSC(P.keyer.WPM,AMP,[F1,F2],FS)
        P.keyer.sidetone = P.osc

        if sys.version_info[0]==3:
            P.q2     = queue.Queue(maxsize=0)
        else:
            P.q2     = Queue.Queue(maxsize=0)
            
        sidetone = threading.Thread(target=sidetone_executive, args=(P,),\
                                    name='Sidetone Osc')
        sidetone.setDaemon(True)
        sidetone.start()
        P.threads.append(sidetone)
        
    else:
        P.q2=None
        P.osc=None


def sidetone_executive(P):
    print('SIDETONE Exec started ...')

    while not P.Stopper.isSet():
        if P.q2.qsize()>0:
            msg = P.q2.get()
            P.q2.task_done()
            msg = msg.replace('[LOG]','')
            print('SIDETONE Exec: msg=',msg)
            if P.osc.enabled:
                P.osc.send_cw(msg,P.keyer.WPM,0,P.SIDETONE)
        else:
            time.sleep(0.1)
                
    print('SIDETONE Done.')
        

class SIDETONE_OSC():
    def __init__(self,WPM,AMP,F0,FS):

        print("\nCreating code practice osc ...")
        self.started = False
        self.enabled = False
        self.AMP=AMP
        if type(F0) is list:
            self.F0=F0
        else:
            self.F0=[F0]
        self.FS=float(FS)

        # Generate sigs
        self.gen_elements(WPM,0)
        
        # Use non-blocking audio player
        self.rb     = dsp.ring_buffer2('Audio0',32*1024)
        self.rb2    = dsp.ring_buffer2('Audio1',32*1024)
        self.player = dsp.AudioIO(None,int(self.FS),self.rb,None,'B',True)

    #def change_freq():
    #    self.gen_elements(self.WPM,1-self.nfrq)

    def start(self):
        self.player.start_playback(0,False)
        self.started = True
        self.enabled = True
        
    def pause(self):
        self.player.pause()
        self.enabled = False
        
    def resume(self):
        self.player.resume()
        self.enabled = True
        
    # Signal generation 
    def gen_elements(self,WPM,nfrq):
        self.WPM=WPM
        self.nfrq=nfrq

        dotlen=1.2/self.WPM
        Ndit = int( self.FS*dotlen + 0.5)
        tt = np.arange(3*Ndit) / self.FS
        self.dah = self.AMP*np.sin(2 * np.pi * self.F0[self.nfrq] * tt)
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
    def send_cw(self,msg,WPM,nfrq,AUDIO_ACTIVE):
        print('SIDETONE->SEND_CW:  msg=',msg,len(msg),AUDIO_ACTIVE)

        # Check for speed or freq change
        if WPM != self.WPM or nfrq!=self.nfrq:
            self.gen_elements(WPM,nfrq)

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
                    if AUDIO_ACTIVE and self.enabled:
                        self.rb.push(x)
                    self.rb2.push(x)

                # Effect spacing between letters - we've already added one short space
                # so we only need 2 more to effect char spacing
                x = np.concatenate( (self.space,self.space) )
                if AUDIO_ACTIVE and self.enabled:
                    self.rb.push(x)                         # Computer Audio
                self.rb2.push(x)                            # Sidetone for capture
                

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
    osc = SIDETONE_OSC(WPM,AMP,F1,FS)
    
    osc.send_cw('Test',WPM)
    time.sleep(5)
    osc.send_cw('=',WPM)
    time.sleep(1)
    #osc.quit()
    
        
