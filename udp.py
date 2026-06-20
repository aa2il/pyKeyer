#!/usr/bin/env -S uv run --script
#########################################################################################
#
# udp.py - Rev. 1.0
# Copyright (C) 2022-6 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
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
from datetime import datetime
from rig_io.ft_tables import bands
import socket
import uuid    

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



# Function to construct UDP contact info packet - similar to N1MM
# See    https://n1mmwp.hamdocs.com/appendices/external-udp-broadcasts/
def contact_info_packet(P,qso):
    print('CONTACT INFO PACKET: qso=',qso)

    ts = datetime.strptime( qso["QSO_DATE_OFF"] +" "+ qso["TIME_OFF"] , "%Y%m%d %H%M%S").strftime("%Y-%m-%d %H:%M:%S")
    band1=qso['BAND']
    f=bands[band1]['CW1']
    band2=str(f/1000).replace('.0','')

    rx=str( int( 1000*float( qso['FREQ_RX'] ) ) )
    tx=str( int( 1000*float( qso['FREQ'] ) ) )

    exch_in  = qso['SRX_STRING'].replace(',',' ')
    exch_out = qso['STX_STRING'].replace(',',' ')

    if 'RST_SENT' in qso:
        rst_out = qso['RST_SENT']
    else:
        rst_out = '599'
    
    if 'RST_RCVD' in qso:
        rst_in = qso['RST_RCVD']
    else:
        rst_in = '599'
    
    pkt='<?xml version="1.0" encoding="utf-8"?>\n' +\
        '<contactinfo>\n' +\
        '\t<app>pyKeyer</app>\n' +\
        '\t<contestname>'+qso['CONTEST_ID']+'</contestname>\n' +\
        '\t<timestamp>'+ts+'</timestamp>\n'+\
        '\t<mycall>'+P.SETTINGS['MY_CALL']+'</mycall>\n' +\
        '\t<band>'+band2+'</band>\n' +\
        '\t<rxfreq>'+rx+'</rxfreq>\n' +\
        '\t<txfreq>'+tx+'</txfreq>\n' +\
        '\t<operator>'+P.SETTINGS['MY_OPERATOR']+'</operator>\n' +\
        '\t<mode>'+qso['MODE']+'</mode>\n' +\
        '\t<call>'+qso['CALL']+'</call>\n' +\
        '\t<snt>'+rst_out+'</snt>\n' +\
        '\t<rcv>'+rst_in+'</rcv>\n'

    if 'QTH' in qso:
        pkt += '\t<qth>'+qso['QTH']+'</qth>\n'
    
    if 'NAME' in qso:
        pkt += '\t<name>'+qso['NAME']+'</name>\n'

    """
    pkt += '\t<sntnr>0</sntnr>\n' +\
        '\t<rcvnr>0</rcvnr>\n' +\
        '\t<gridsquare></gridsquare>\n' +\
        '\t<section></section>\n' +\
        '\t<comment></comment>\n' +\
        '\t<power></power>\n' +\
        '\t<misctext></misctext>\n' +\
        '\t<zone>0</zone>\n' +\
        '\t<prec></prec>\n' +\
        '\t<ck>0</ck>\n' +\
        '\t<radionr>1</radionr>\n' +\
        '\t<run1run2>1<run1run2>\n' +\
        '\t<RoverLocation></RoverLocation>\n' +\
        '\t<RadioInterfaced>1</RadioInterfaced>\n' +\
        '\t<NetworkedCompNr>0</NetworkedCompNr>\n' +\
        '\t<IsOriginal>False</IsOriginal>\n' +\
        '\t<NetBiosName></NetBiosName>\n' +\
        '\t<IsRunQSO>0</IsRunQSO>\n'
    """
    
    pkt += '\t<StationName>'+socket.gethostname()+'</StationName>\n' +\
        '\t<ID>'+uuid.uuid4().hex+'</ID>\n' +\
        '\t<IsClaimedQso>1</IsClaimedQso>\n' +\
        '\t<oldtimestamp>'+ts+'</oldtimestamp>\n' +\
        '\t<oldcall>'+qso['CALL']+'</oldcall>\n' +\
        '\t<exchangel>'+exch_in+'</exchangel>\n' +\
        '\t<SentExchange>'+exch_out+'</SentExchange>\n' +\
        '</contactinfo>'

    return pkt


############################################################################################

# If this file is called as main, read a qso from the log a test contact info packet
if __name__ == '__main__':
    print('\nHello!')

    from settings import read_settings
    from pprint import pprint
    from fileio import parse_adif
    from tcp_server import UDP_Broadcast_Server,BROADCAST_UDP_PORT
    import time

    # Read settings
    class PARAMS:
        def __init__(self):
            self.SETTINGS,self.RCFILE = read_settings('.keyerrc')
            my_call = self.SETTINGS['MY_CALL']
            print('my_call=',my_call)
            self.LOG_FILE=my_call+'.adif'

    P=PARAMS()
    print("P=")
    pprint(vars(P))

    # Read list of QSOs
    qsos = parse_adif(P.LOG_FILE,upper_case=True,verbosity=0)
    print('nqsos=',len(qsos))

    # Create a contact info packet for the last QSO
    qso=qsos[-1]
    pkt=contact_info_packet(P,qso)
    print('pkt=',pkt)

    # Broadcast it - if HamConnect is running, it will receive it
    P.udp_server = UDP_Broadcast_Server(P,None,BROADCAST_UDP_PORT,Server=True,
                              Handler=UDP_msg_handler)
    time.sleep(1)
    P.udp_server.Broadcast(pkt,DEBUG=True)
    time.sleep(1)
    
