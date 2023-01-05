#########################################################################################
#
# udp.py - Rev. 1.0
# Copyright (C) 2022 by Joseph B. Attili, aa2il AT arrl DOT net
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

#from tcp_client import *
#from tcp_server import *
from tkinter import END

#########################################################################################

# UDP Message handler for pyKeyer
def UDP_msg_handler(self,sock,msg):
    print('UDP Message Handler: msg=',msg.rstrip())
    P=self.P

    msgs=msg.split('\n')
    for m in msgs:
        print('UDP MSG HANDLER: m=',m,len(m))

        mm=m.split(':')
        if mm[0]=='Call':
        
            # Call:callsign:VFO
            call = mm[1]
            vfo  = mm[2]
            print('UDP Message Handler: Setting call to:',call,vfo,P.gui.contest)
            call2=P.gui.get_call()
            if call!=call2 and vfo=='A':
            
                P.gui.Clear_Log_Fields()
                P.gui.call.insert(0,call)
                P.gui.dup_check(call)
                if P.gui.contest or True:
                    P.gui.get_hint(call)
                    if P.AUTOFILL:
                        P.KEYING.insert_hint()
                if P.USE_SCP and False:
                    # Not why we would need this?
                    scps,scps2 = P.KEYING.SCP.match(call,VERBOSITY=0)
                    P.gui.scp.delete(0, END)
                    P.gui.scp.insert(0, scps)

            elif vfo=='B':

                P.gui.OnDeckCircle.delete(0, END)
                P.gui.OnDeckCircle.insert(0,call)

            elif mm[0]=='Sat':
        
                # Sat:sat_name
                sat=mm[1]
                print('UDP Message Handler: Setting SAT to:',sat)
                P.gui.set_satellite(sat)
    
            elif mm[0]=='Name':
        
                # Name:Client_name
                name=mm[1]
                print('UDP Message Handler: Client Name=',name)
    
    return


