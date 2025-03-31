import Configuration
from Messages import *

import socket
from typing import Set



# ======================================================================================================================
class Client(object):
    '''
    
    '''

    def __init__(self) -> None:
        '''
        
        '''
        # Connection information
        self.connections: dict[str, socket.socket] = dict()
        self.packet_size:         int = Configuration.DEFAULT_PACKET_SIZE
        self.min_reroute_timeout: int = Configuration.DEFAULT_MIN_REROUTE_TIMEOUT
        self.max_reroute_timeout: int = Configuration.DEFAULT_MAX_REROUTE_TIMEOUT
        self.port:                int = Configuration.DEFAULT_PORT
    

    def connect(self, ip: str, port: int) -> None | str:
        '''Attempt outgoing connection to external server.

        Args:
            ip (str): IPv4 address of target server.
            port (int): Port server is listening for connections on.
        '''
        try:
            if(ip not in self.connections.keys()):
                new_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_conn.connect((ip, port))
                self.connections[ip] = new_conn
                return self.recv(ip).decode()
        except Exception as e:
            print(f"[ERR] Unable to establish forward connection with {ip} on {port}\n |-> {e}")
            return None

    
    def disconnect(self, ip: str) -> None:
        '''Close outgoing connection with server.

        Args:
            ip (str): IPv4 address of connection to be closed.
        
        '''
        try:
            self.connections[ip].close()
            self.connections.pop(ip)
            print(f"[INFO] Disconnected from {ip}")
        except Exception as e:
            print(f"[ERR] Unable to disconnect from {ip}\n |-> {e}")

    
    def send(self, ip: str, data: bytes | str) -> None:
        '''Send data over an open connection.

        Args:
            ip (str): IPv4 address of associated connection.
            data (bytes | str): Data or string message to be sent to destination.
        
        '''
        # Safeguard; data _should_ be bytes
        if(data == str):
            data = data.encode()
        self.connections[ip].send(data)

    
    def recv(self, ip: str) -> bytes:
        '''Receive data from a specific connection.

        Args:
            ip (str): IPv4 address client anticipates data from.
        
        '''
        data = self.connections[ip].recv(2048)
        return data

    
    def console_mode(self, ip: str) -> None:
        '''Enter console mode for string-based entry of data.

        Args:
            ip (str): IPv4 address to send and receive data over.
        
        '''
        msg = ''
        while True:
            msg = input("> ")
            self.send(ip, msg.encode())
            response = self.recv(ip)
            if(response == MSG_EXIT):
                break



# ======================================================================================================================
if __name__ == "__main__":
    print("[Running Stand-Alone Client]")
    client = Client()
    client.connect("127.0.0.1", 7877)
    client.console_mode("127.0.0.1")
    client.disconnect("127.0.0.1")
    