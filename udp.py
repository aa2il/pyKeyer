#########################################################################################
#
# udp.py - Rev. 1.0
# Copyright (C) 2022-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# UDP messaging for pyKeyer.
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
#########################################################################################

from tkinter import END

#########################################################################################

# Routine to handle details of inserting a new call - e.g. when op clicks on a spot
def insert_new_call(self,call,vfo):

    P=self.P
    MY_CALL = P.SETTINGS['MY_CALL']
    call2=P.gui.get_call()  
    if call!=call2 and vfo=='A':
            
        P.gui.Clear_Log_Fields()
        if call!=MY_CALL:
            P.gui.call.insert(0,call)
            P.gui.dup_check(call)
            P.gui.get_hint(call)
            if P.AUTOFILL:
                P.KEYING.insert_hint()

                # This actually works BUT fldigi doesn't handle revisions correctly?!
                if P.sock.rig_type=='FLDIGI' and P.sock.fldigi_active and False:
                    print('Setting FLDIGI log fields ...')
                    P.gui.Read_Log_Fields()

    elif vfo=='B':

        P.gui.OnDeckCircle.delete(0, END)
        if call!=MY_CALL:
            P.gui.OnDeckCircle.insert(0,call)
                


# UDP Message handler for pyKeyer
def UDP_msg_handler(self,sock,msg):
    print('UDP Message Handler: msg=',msg.rstrip(),'\nsock=',sock)
    P=self.P

    msgs=msg.split('\n')
    for m in msgs:
        mm=m.split(':')
        print('UDP MSG HANDLER: m=',m,'\tmm[0]=',mm[0])

        if mm[0]=='Call':
        
            # Op clicked on a spot in the SDR or Bandmap
            # Call:callsign:VFO
            call = mm[1]
            vfo  = mm[2]
            print('UDP Message Handler: Setting call to:',call,vfo,P.gui.contest)
            insert_new_call(self,call,vfo)
            return

        elif mm[0]=='Sat':
        
            # Sat:sat_name
            sat=mm[1]
            print('UDP Message Handler: Setting SAT to:',sat)
            P.gui.set_satellite(sat)
            return
    
        elif mm[0]=='Name':
        
            # Name:Client_name
            if mm[1]=='?':
                print('UDP MSG HANDLER: Server name query')
                msg2='Name:KEYER\n'
                sock.send(msg2.encode())
            else:
                print('UDP MSG HANDLER: Client name is',mm[1])
            return
                
        elif mm[0] in ['RunFreq','SpotFreq'] and mm[1]=='TRY':
        
            # RunFreq:TRY:freq
            frq=float(mm[2])
            print('UDP Message Handler: '+mm[0]+' Tuning to Freq =',frq)
            P.gui.sock.set_freq(frq)

            # SpotFreq:TRY:freq:call:vfo
            if mm[0]=='SpotFreq' and True:
                call = mm[3]
                vfo  = mm[4]
                print('UDP Message Handler: Setting call to:',call,vfo,P.gui.contest)
                insert_new_call(self,call,vfo)
            
            return
                    
        print('UDP MSG HANDLER: Not sure what to do with this',mm)


