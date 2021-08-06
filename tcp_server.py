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
            time.sleep(1)
            
            # Get list of sockets 
            #print('Getting list')
            #readable,writeable,inerror = select.select(self.socks,self.socks,self.socks,0)
            readable,writeable,inerror = select.select(self.socks,[],[],0)
            #print('readable=',readable,'\twriteable=',writeable,'\tinerror=',inerror)
            
            # iterate through readable sockets
            #i=0
            for sock in readable:
                if sock is self.tcpServer:
                    
                    # Accept new connection
                    conn, addr = self.tcpServer.accept()
                    print('\r{}:'.format(addr),'connected')
                    readable.append(conn)
                    self.socks.append(conn)

                else:
                    
                    # Read from a client
                    try:
                        data = sock.recv(self.BUFFER_SIZE)
                    except:
                        print('Listener: Problem with socket - closing')
                        print(sock)
                        data=None
                
                    if not data:
                        try:
                            print('\r{}:'.format(sock.getpeername()),'disconnected')
                            sock.close()
                        except:
                            pass
                        readable.remove(sock)
                        self.socks.remove(sock)
                    else:
                        print('\r{}:'.format(sock.getpeername()),data)
                        if self.msg_handler:
                            self.msg_handler(data.decode())
                        
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

