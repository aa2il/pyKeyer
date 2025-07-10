################################################################################
#
# ProcessChars.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Executive thread to process individual characters.
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

import sys
import time
from nano_io import *
from tkinter import END
from utilities import error_trap

################################################################################

# Set up separate process that actualy does the keying.
# We do this so that the GUI process is not blocked by the keying.
def process_chars(P):
    P.last_time  = 0
    keyer     = P.keyer
    lock      = P.lock1
    q         = P.q
    VERBOSITY = 0
    P.nano_txt = ''

    P.last_char_time=time.time()
    P.need_eol=False
    nerrors = 0
    
    while not P.Stopper.isSet() and nerrors<10:

        if VERBOSITY>0:
            print('PROCESSS_CHARS: Checking msg queue ... q-size=',q.qsize())
            
        # Anything available to send?
        if q.qsize()>0:
            if VERBOSITY>0:
                print('PROCESSS_CHARS: Get txt...')
            txt=q.get()
            q.task_done()

            # Check keyer speed on radio - can't do this here since we're not in the main gui loop!
            if VERBOSITY>0:
                print('PROCESSS_CHARS: txt=',txt)
            this_time = time.time();
            if this_time - P.last_time>0.1 and not P.PRACTICE_MODE and False:
                if VERBOSITY>0:
                    print('PROCESSS_CHARS: this_time=',this_time,P.last_time)
                P.last_time=this_time
                try:
                    if VERBOSITY>0:
                        print('PROCESSS_CHARS: Read WPM ...')
                    WPM = P.sock.read_speed()
                    if VERBOSITY>0:
                        print('PROCESSS_CHARS: WPM=',WPM,P.WPM)
                    if WPM!=P.WPM2 and WPM>=5:
                        print('PROCESSS_CHARS: Set WPM=',WPM)
                        keyer.set_wpm(WPM)
                        P.gui.WPM_TXT.set(str(WPM))
                except: 
                    error_trap('PROCESS CHARS - Unable to check radio keyer speed')

            print('PROCESSS_CHARS: txt=',txt,'\tWPM=',keyer.WPM)

            # Check if we need to send this sidetone also - chars are already sent if we're in practice mode
            if P.q2 and not P.PRACTICE_MODE and P.SIDETONE:
                txt2=''
                keep=True
                for ch in txt:
                    if ch=='[':
                        keep=False          # Skip over command sequences
                    elif ch==']':
                        keep=True
                    elif keep:
                        txt2+=ch
                print('\n=============== Pushing txt to q2:',txt2)
                P.q2.put(txt2)
                
            # Timing is critical so we make sure we have control
            lock.acquire()
            keyer.send_msg(txt)
            lock.release()

        else:

            # Check NanoIO device for any messages
            if P.USE_KEYER:

                if VERBOSITY>0:
                    print('PROCESSS_CHARS: Checking rx from keyer ...')

                # This has thrown an error in the past
                # Probably because keyer port gets closed but its not properly noted
                try:
                    if P.ser and P.ser.in_waiting>0:              # The error is with "in_waiting"
                        if VERBOSITY>0:
                            print('PROCESSS_CHARS: Getting data from keyer ... echo=',P.NANO_ECHO,P.ser,P.ser.in_waiting)
                        txt=P.keyer_device.nano_read()
                        if P.NANO_ECHO and len(txt)>0:
                            # Check if its been a while since the last char was received
                            # This won't work properly bx linux is not real-time - need to put this in the keyer
                            if P.WINKEYER or P.K3NG_IO:
                                t=time.time()
                                dt=t-P.last_char_time
                                #print(t,last_char_time,dt,10*P.keyer.dotlen,need_eol)
                                if P.need_eol and dt>1.5:      # 10*P.keyer.dotlen:
                                    txt='\n'+txt
                                    P.need_eol=False
                                else:
                                    P.need_eol=True
                                P.last_char_time=t
                            
                            # Check if user has responded to current paddling text
                            if P.SENDING_PRACTICE and '\n' in txt:
                                P.gui.PaddlingWin.responded=True
                                print('PROCESS CHARS: repsonded=',P.gui.PaddlingWin.responded)
                                
                            # Add a <CR/LF> if we are echoing back a command
                            if P.NANO_IO and txt[0]=='~' and txt[-1] in ['u','s']:
                                txt+='\n'

                            # Put it in the big text box also
                            P.gui.txt.insert(END, txt)
                            P.gui.txt.see(END)
                            P.gui.root.update_idletasks()
                            P.nano_txt += txt
                            """
                            if '\n' in txt:
                                print('NANO: ',P.nano_txt.strip())
                                #P.gui.fp_txt.write('NANO: %s\n' % (nano_txt) )
                                #P.gui.fp_txt.flush()
                                P.nano_txt = ''
                            """

                            # Get text
                            if P.SENDING_PRACTICE:
                                P.gui.PaddlingWin.check_response(txt)

                                
                        if VERBOSITY>0:
                            print('PROCESSS_CHARS: Getting data from keyer ... txt=',txt)
                    else:
                        time.sleep(0.1)
                        
                except: 
                    error_trap('PROCESS CHARS - Unknown error?????',1)
                    print('\tP.ser=',P.ser)
                    print('\tP.keyer_device.ser=',P.keyer_device.ser)
                    if P.ser and P.keyer_device.ser==None:
                        print('\n\t*** Inconsistency found in keying port - status fudged! ***\n')
                        P.ser=None
                    time.sleep(0.1)
                    nerrors += 1
                    #sys.exit(0)
                    
            else:
                time.sleep(0.1)
        
    if nerrors>=10:
        print('\n*** PROCESSS_CHARS - Too many erros - giving up! ***')
        #sys.exit(0)
        P.gui.Quit()
        
    print('PROCESSS_CHARS Done.')
