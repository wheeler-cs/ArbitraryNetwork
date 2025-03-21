from Configuration import Configuration
from Server import Server
from Client import Client

import socket
from typing import Set


class AdHocNetwork(object):
    '''
    
    '''
    
    def __init__(self) -> None:
        '''
        
        '''
        self.config = Configuration("cfg")
        self.peer_nodes: Set[str] = set()
        self.server = Server(self.config)
        self.client = Client(self.config)
        self.init_server()
        self.init_client()

    
    def init_server(self) -> None:
        '''
        
        '''
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('', self.config.listen_port))
        print(f"[INFO] Server: Bound to port {self.config.listen_port}\n[INFO] Server: Listening for peers")
        self.server.listen(self.config.server_max_clients)

    
    def init_client(self) -> None:
        '''
        
        '''
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    
    def start_server(self) -> None:
        '''
        
        '''
        while(True):
            conn, addr = self.server.accept()
            print(f"[INFO] Server: Connected to {addr}")
            conn.close()
            break

    
    def client_conn(self, ip: str, port: int) -> None:
        '''
        
        '''
        self.client.connect(())

    
    def shutdown(self) -> None:
        '''
        
        '''
        self.server.close()
        self.client.close()



if __name__ == "__main__":
    ahn = AdHocNetwork()
    ahn.start_server()
