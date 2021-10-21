#! /usr/bin/python3
################################################################################
#
# tcp_server.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
#    Simple tcp server to effect allow clients to communicate to app.
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
import socket 
from threading import Thread,Event
import time
import select

VERBOSITY=0

################################################################################

# TCP Server class
class TCP_Server(Thread):
    
    def __init__(self,host,port,BUFFER_SIZE = 1024,Stopper=None,Handler=None): 
        Thread.__init__(self)
        if not host:
            host='127.0.0.1'
        self.host=host
        self.port=port
        self.BUFFER_SIZE = BUFFER_SIZE
        self.msg_handler=Handler
        
        print('TCP Server:',host,port)

        self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.tcpServer.bind((host,port))

        if Stopper==None:
            self.Stopper = Event()
        else:
            self.Stopper = Stopper

        self.socks = [self.tcpServer]        

    # Function to listener for new connections and/or data from clients
    def Listener(self): 
        print("Listener: Waiting for connections from TCP clients..." )
        self.tcpServer.listen(4)
        
        while not self.Stopper.isSet():
            if VERBOSITY>0:
                print('TCP_SERVER - Listener - Hey 1')
            time.sleep(1)
            
            # Get list of sockets 
            readable,writeable,inerror = select.select(self.socks,[],[],0)
            if VERBOSITY>0:
                print('TCP_SERVER - Listener - readable=',readable,  \
                      '\twriteable=',writeable,'\tinerror=',inerror)
            
            # iterate through readable sockets
            #i=0
            for sock in readable:
                if VERBOSITY>0:
                    print('TCP_SERVER - Listener - Hey 2')
                if sock is self.tcpServer:
                    if VERBOSITY>0:
                        print('TCP_SERVER - Listener - Hey 3')
                    
                    # Accept new connection
                    conn, addr = self.tcpServer.accept()
                    #conn.settimeout(2)
                    conn.setblocking(0)
                    print('\r{}:'.format(addr),'connected')
                    readable.append(conn)
                    self.socks.append(conn)

                else:

                    # Read from a client
                    #timeout=False
                    try:
                        if VERBOSITY>0:
                            print('TCP_SERVER - Listener - Hey 4a')
                        ready = select.select([sock], [], [], 1)
                        if ready[0]:
                            data = sock.recv(self.BUFFER_SIZE)
                        else:
                            data=None
                        if VERBOSITY>0:
                            print('TCP_SERVER - Listener - Hey 4b - ready=',ready)
                    #except socket.timeout:
                    #    if VERBOSITY>0:
                    #        print('TCP_SERVER - Listener - Socket timeout')
                    #    data=None
                    #    timeout=True
                    except Exception as e: 
                        print('Listener: Problem with socket - closing')
                        print( str(e) )
                        print(sock)
                        data=None
                
                    if data:
                        # We received a message from a client
                        print('\r{}:'.format(sock.getpeername()),data)
                        if self.msg_handler:
                            self.msg_handler(data.decode())
                            
                    elif ready[0]:
                        # The client seemed to send a msg but we didn't get it
                        try:
                            print('\r{}:'.format(sock.getpeername()),'disconnected')
                            sock.close()
                        except:
                            pass
                        readable.remove(sock)
                        self.socks.remove(sock)
                    else:
                        # Nothing to see here
                        pass
                        
            # a simple spinner to show activity
            #i += 1
            #print('/-\|'[i%4]+'\r',end='',flush=True)

        # Close socket
        self.tcpServer.close()
        print('Listerner: Bye bye!')

    # Function to broadcast a message to all connected clients
    def Broadcast(self,msg):

        # Get list of sockets 
        readable,writeable,inerror = select.select([],self.socks,[],0)
            
        for sock in writeable:
            #print(sock)
            addr = sock.getsockname()
            print('Sending',msg,'to',addr,'...')
            try:
                sock.send(msg.encode())
            except:
                print('Broadcast: Problem with socket')
                print(sock)
                
################################################################################

# Test program                
if __name__ == '__main__':
    TCP_IP = '127.0.0.1' 
    TCP_PORT = 2004 

    server = TCP_Server(TCP_IP,TCP_PORT)
    worker = Thread(target=server.Listener, args=(), name='TCP Server' )
    worker.setDaemon(True)
    worker.start()
    
    #thread.join()
    while True:
        #print('zzzzzzzzzzzzzzzzz....')
        server.Broadcast('Heartbeat')
        time.sleep(1)
        
    print('Joining ...')
    worker.join()
    print('Done.')

    sys.exit(0)

