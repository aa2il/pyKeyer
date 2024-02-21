#! /usr/bin/python3 -u
################################################################################
#
# ProcessChars.py - Rev 1.0
# Copyright (C) 2021-4 by Joseph B. Attili, aa2il AT arrl DOT net
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

import time
from nano_io import *
from tkinter import END
import traceback

################################################################################

# Set up separate process that actualy does the keying.
# We do this so that the GUI process is not blocked by the keying.
def process_chars(P):
    last_time = 0
    keyer     = P.keyer
    lock      = P.lock1
    q         = P.q
    VERBOSITY = 0
    nano_txt  = ''

    last_char_time=time.time()
    need_eol=False
    
    while not P.Stopper.isSet():

        if VERBOSITY>0:
            print('PROCESSS_CHARS: Checking msg queue ...',q.qsize())
            
        # Anything available?
        if q.qsize()>0:
            if VERBOSITY>0:
                print('PROCESSS_CHARS: Get txt...')
            txt=q.get()
            q.task_done()

            # Check keyer speed on radio - can't do this since we're not in the main gui loop!
            if VERBOSITY>0:
                print('PROCESSS_CHARS: txt=',txt)
            this_time = time.time();
            if this_time - last_time>0.1 and not P.PRACTICE_MODE and False:
                if VERBOSITY>0:
                    print('PROCESSS_CHARS: this_time=',this_time,last_time)
                last_time=this_time
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
                except Exception as e: 
                    print('PROCESS CHARS - Unable to check radio keyer speed')
                    print( str(e) )

            print('PROCESSS_CHARS: txt=',txt,'\tWPM=',keyer.WPM)

            # Check if we need to send this sidetone also
            if P.q2 and not P.PRACTICE_MODE and (P.SIDETONE or P.CAPTURE):
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
                try:
                    if P.ser and P.ser.in_waiting>0:
                        if VERBOSITY>0:
                            print('PROCESSS_CHARS: Getting data from keyer ... echo=',P.NANO_ECHO,P.ser,P.ser.in_waiting)
                        txt=P.keyer_device.nano_read()
                        if P.NANO_ECHO and len(txt)>0:
                            # Check if its been a while since the last char was received
                            # This won't work properly bx linux is not real-time - need to put this in the keyer
                            if P.WINKEYER or P.K3NG_IO:
                                t=time.time()
                                dt=t-last_char_time
                                #print(t,last_char_time,dt,10*P.keyer.dotlen,need_eol)
                                if need_eol and dt>1.5:      # 10*P.keyer.dotlen:
                                    txt='\n'+txt
                                    need_eol=False
                                else:
                                    need_eol=True
                                last_char_time=t
                            
                            # Check is user has responded to current paddling text
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
                            nano_txt += txt
                            if '\n' in txt:
                                print('NANO: ',nano_txt.strip())
                                #P.gui.fp_txt.write('NANO: %s\n' % (nano_txt) )
                                #P.gui.fp_txt.flush()
                                nano_txt = ''

                            # Get text
                            if P.SENDING_PRACTICE:
                                P.gui.PaddlingWin.check_response(txt)

                                
                        if VERBOSITY>0:
                            print('PROCESSS_CHARS: Getting data from keyer ... txt=',txt)
                    else:
                        time.sleep(0.1)
                        
                except Exception as e: 
                    print("\nPROCESS CHARS - *** ERROR ***")
                    print('e=',e,'\n')
                    traceback.print_exc()
                    time.sleep(0.1)

                    
            else:
                time.sleep(0.1)
        
    print('PROCESSS_CHARS Done.')
