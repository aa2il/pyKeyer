#! /usr/bin/python3 -u
################################################################################
#
# ProcessChars.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
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
    
    while not P.Stopper.isSet():

        if VERBOSITY>0:
            print('PROCESSS_CHARS: Checking ...',q.qsize())
            
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
            if P.NANO_IO:
                
                if VERBOSITY>0:
                    print('PROCESSS_CHARS: Nano 1')
                
                if P.ser and P.ser.in_waiting>0:
                    if VERBOSITY>0:
                        print('PROCESSS_CHARS: Nano 2A')
                    txt=nano_read(P.ser)
                    if VERBOSITY>0:
                        print('PROCESSS_CHARS: Nano 3',P.NANO_ECHO)
                    if P.NANO_ECHO:
                        # Put it in the big text box also
                        try:
                            if VERBOSITY>0:
                                print('PROCESSS_CHARS: Nano 4')
                            #P.gui.txt.insert(END, txt+'\n')
                            P.gui.txt.insert(END, txt)
                            P.gui.txt.see(END)
                            P.gui.root.update_idletasks()
                            nano_txt += txt
                            if '\n' in txt:
                                print('\nNANO: ',nano_txt)
                                #P.gui.fp_txt.write('NANO: %s\n' % (nano_txt) )
                                #P.gui.fp_txt.flush()
                                nano_txt = ''
                            if VERBOSITY>0:
                                print('PROCESSS_CHARS: Nano 5')
                        except Exception as e: 
                            print( str(e) )
                else:
                    time.sleep(0.1)
                    
                if VERBOSITY>0:
                    print('PROCESSS_CHARS: Nano 6')
            else:
                time.sleep(0.1)
        
    print('PROCESSS_CHARS Done.')



