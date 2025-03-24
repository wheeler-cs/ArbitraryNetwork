import Configuration

import socket
from typing import Set



# ======================================================================================================================
class Client(object):
    '''
    
    '''

    def __init__(self) -> None:
        '''
        
        '''
        self.connections: dict[str, socket.socket] = dict()
        self.packet_size:         int = Configuration.DEFAULT_PACKET_SIZE
        self.min_reroute_timeout: int = Configuration.DEFAULT_MIN_REROUTE_TIMEOUT
        self.max_reroute_timeout: int = Configuration.DEFAULT_MAX_REROUTE_TIMEOUT
        self.port:                int = Configuration.DEFAULT_PORT
    

    def connect(self, ip: str, port: int) -> None:
        '''
        
        '''
        try:
            if(ip not in self.connections.keys()):
                new_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_conn.connect((ip, port))
                self.connections[ip] = new_conn
            else:
                raise Exception()
        except Exception as e:
            print(f"[ERR] Unable to establish forward connection with {ip} on {port}\n|-> Reason: {e}")

    
    def disconnect(self, ip: str) -> None:
        '''
        
        '''
        try:
            self.connections[ip].close()
            self.connections.pop(ip)
        except Exception as e:
            print(f"[ERR] Unable to disconnect from {ip}\n|-> Reason: {e}")

    
    def send(self, ip: str, data: bytes) -> None:
        '''
        
        '''
        self.connections[ip].send(data)

    
    def recv(self, ip: str) -> bytes:
        '''
        
        '''
        data = self.connections[ip].recv(2048)
        return data

    
    def console_mode(self, ip) -> None:
        msg = ''
        while msg != "exit":
            msg = input("> ")
            self.send(ip, msg)
            print(self.recv(ip).decode())



# ======================================================================================================================
if __name__ == "__main__":
    print("[Running Stand-Alone Client]")
    client = Client()
    client.connect("127.0.0.1", 7877)
    client.console_mode("127.0.0.1")
    client.disconnect("127.0.0.1")
    