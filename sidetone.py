#! /usr/bin/python
############################################################################################
#
# sidetone.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
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

import numpy as np
from cw_keyer import morse
import sys
import time
import threading
if sys.version_info[0]==3:
    import queue
else:
    import Queue
from sig_proc import ring_buffer2
from audio_io import AudioIO,pgPLAYER    

###################################################################

# User params
FS = 8000    # 48000              # Playback rate
F1 = 680                # My pitch
F2 = 700                # Caller's pitch
AMP = 0.5

################################################################################

class AUDIO_SIDETONE():
    
    def __init__(self,P):
    
        print('AUDIO SIDETONE: Init ...')
        self.P=P
        self.started = False
        self.enabled = False
        self.osc = SIDETONE_OSC(P.keyer.WPM,AMP,[F1,F2],FS,P.USE_PYGAME)
        P.keyer.sidetone = self.osc
        P.osc=self.osc
        self.player=self.osc.player

        if sys.version_info[0]==3:
            self.q2     = queue.Queue(maxsize=0)
        else:
            self.q2     = Queue.Queue(maxsize=0)
        P.q2=self.q2

        self.sidetone_exec = threading.Thread(target=self.sidetone_executive, args=(),\
                                              name='Sidetone Osc')
        self.sidetone_exec.setDaemon(True)
        if not hasattr(P,'threads'):
            P.threads=[]
        P.threads.append(self.sidetone_exec)
        if not hasattr(P,'Stopper'):
            P.Stopper = threading.Event()

    def start(self):
        print('AUDIO SIDETONE: Start ...',self.started)
        if self.P.SIDETONE:
            print('AUDIO_SIDETONE: Player started...',self.P.SIDETONE)
            self.player.start_playback(0,False)
        #self.osc.start()
        if not self.started:
            print('AUDIO SIDETONE: Starting Exec ...')
            self.sidetone_exec.start()
        self.started = True
        self.enabled = True
        
    def pause(self):
        print('AUDIO SIDETONE: Pause ...')
        self.player.pause()
        self.enabled = False
        #self.osc.pause()
        
    def resume(self):
        print('AUDIO SIDETONE: Resume ...')
        self.player.resume()
        self.enabled = True
        #self.osc.resume()

    def push(self,txt):
        self.q2.put(txt)

    def abort(self):
        self.osc.abort()
        
    def sidetone_executive(self):
        print('AUDIO SIDETONE: Exec started ...')
        P=self.P

        while not P.Stopper.isSet():
            if P.q2.qsize()>0:
                msg = P.q2.get()
                P.q2.task_done()
                msg = msg.replace('[LOG]','')
                print('SIDETONE EXEC: msg=',msg)
                P.osc.send_cw(msg,P.keyer.WPM,0,P.SIDETONE)
            else:
                time.sleep(0.1)
                
        print('SIDETONE EXEC Done.')
        

class SIDETONE_OSC():
    def __init__(self,WPM,AMP,F0,FS,USE_PYGAME=False):

        self.AMP=AMP
        if type(F0) is list:
            self.F0=F0
        else:
            self.F0=[F0]
        self.FS=float(FS)
        print("\nCreating code practice osc ... FS=",self.FS,'\tF0=',self.F0)
        self.Stopper = threading.Event()

        # Generate sigs
        self.gen_elements(WPM,0)
        
        # Use non-blocking audio player
        BUFF_SIZE=4*32*1024                 # Was 1x
        if USE_PYGAME:
            self.player=pgPLAYER(self.FS)
        else:
            self.rb     = ring_buffer2('Audio0',BUFF_SIZE,PREVENT_OVERFLOW=False)
            #self.rb2    = dsp.ring_buffer2('Audio1',BUFF_SIZE,PREVENT_OVERFLOW=False)         # For capture if we need it
            self.player = AudioIO(None,int(self.FS),self.rb,None,'B',True)

    def get_freq(self,n=None):
        if n==None:
            n=self.nfrq
        return int( self.F0[n] )

    def change_freq(self,fnew,n=None):
        if n==None:
            n=self.nfrq
        self.F0[n] = fnew
        self.gen_elements(self.WPM,n)

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
        VERBOSITY=0

        if VERBOSITY>0:
            print('SIDETONE->SEND_CW:  msg=',msg,len(msg),'\tAUDIO_ACTIVE=',AUDIO_ACTIVE)

        # Check for speed or freq change
        if WPM != self.WPM or nfrq!=self.nfrq:
            self.gen_elements(WPM,nfrq)

        # Loop over all chars
        x=np.array([])
        for char in msg.upper():

            if self.Stopper.isSet():
                self.Stopper.clear()
                break

            try:
                i=ord(char)
                cw=morse[i]
            except:
                print('SIDETONE->SEND_CW: Invalid character',char,'\t',i)
                i=32
                cw=morse[i]
            
            if VERBOSITY>0:
                print('SIDETONE->SEND_CW: Sending *',i,'*',char,'*',cw,'*')
            
            if i>=32:
                # Loop over all elements in this char
                for el in cw:
                    # After each element, we insert a short space to effect element spacing
                    if( el==' ' ):
                        # After each char, 3 short spaces have already been added (see code below).
                        # Hence, we need 4 short spaces to get letter spacing correct (7 short)
                        # This seems too long so we cheat and only 3 short spaces (6 short)
                        x = np.concatenate( (x,self.long_space,self.space) )
                    elif( el=='.' ):
                        x = np.concatenate( (x,self.dit,self.space) )
                    elif( el=='-' ):
                        x = np.concatenate( (x,self.dah,self.space) )

                # Effect spacing between letters - we've already added one short space
                # so we only need 2 more to effect char spacing
                x = np.concatenate( (x,self.space,self.space) )
                
        # Play the message
        if AUDIO_ACTIVE:
            self.player.push(x)
        #self.rb2.push(x)                            # Sidetone for capture
                            
    def abort(self):
        self.Stopper.set()
        self.player.stop()

    def play(self):
        x = np.concatenate( (self.dit,self.space,self.dah,self.space) )
        #data = x.astype(np.float32).tostring()
        data = x.astype(np.float32).tobytes()
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
    
        
