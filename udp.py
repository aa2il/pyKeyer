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

from tcp_client import *

#########################################################################################

# UDP Message handler for pyKeyer
def UDP_msg_handler(self,sock,msg):
    print('UDP Message Handler: msg=',msg.rstrip())
    P=self.P

    msg=msg.split(':')
    if msg[0]=='Call':
        
        # Call:callsign:VFO
        call=msg[1]
        vfo=msg[2]
        print('UDP Message Handler: Setting call to:',call,vfo,P.gui.contest)
        call2=P.gui.get_call()
        if call!=call2 and vfo=='A':
            
            P.gui.Clear_Log_Fields()
            P.gui.call.insert(0,call)
            P.gui.dup_check(call)
            if P.gui.contest:
                P.gui.get_hint(call)
                if P.AUTOFILL:
                    P.KEYING.insert_hint()

        elif vfo=='B':

            P.gui.OnDeckCircle.delete(0, END)
            P.gui.OnDeckCircle.insert(0,call)

    elif msg[0]=='Sat':
        
        # Sat:sat_name
        sat=msg[1]
        print('UDP Message Handler: Setting SAT to:',sat)
        P.gui.set_satellite(sat)
    
    elif msg[0]=='Name':
        
        # Name:Client_name
        name=msg[1]
        print('UDP Message Handler: Client Name=',name)
    
    return


