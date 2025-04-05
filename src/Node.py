from KeyStore import KeyStore
from PeerNode import PeerNode

import json
from os import path
import socket
import threading
from typing import Set


class Node(object):
    '''
    
    '''
    def __init__(self, cfg_dir: str) -> None:
        '''
        
        '''
        # Server variables
        self.server_port:   int              = 0
        self.server_sock:   socket.socket    = None
        self.server_thread: threading.Thread = None
        # Client variables
        self.path_length:   int              = 0
        self.peers:         Set[PeerNode]    = set()
        self.client_sock:   socket.socket    = None
        self.client_thread: threading.Thread = None
        # Cryptographic information
        self.keystore:      KeyStore         = KeyStore()
        # Initialization
        self.load_server_cfg(path.join(cfg_dir, "server.json"))
        self.load_client_cfg(path.join(cfg_dir, "client.json"))
        self.init_components()
        self.start_threads()
    

    def load_server_cfg(self, cfg_file: str) -> None:
        '''
        
        '''
        cfg_data = None
        with open(cfg_file, 'r') as server_cfg:
            cfg_data = json.load(server_cfg)
        self.server_port = cfg_data["connection"]["port"]
        self.keystore.load_server_keys(cfg_data["files"]["public_key"], cfg_data["files"]["private_key"])


    
    def load_client_cfg(self, cfg_file: str) -> None:
        '''

        '''
        cfg_data = None
        with open(cfg_file, 'r') as client_cfg:
            cfg_data = json.load(client_cfg)
        self.keystore.load_client_keys(cfg_data["files"]["public_key"], cfg_data["files"]["private_key"])
        for name in cfg_data["cores"]:
            ip, port = cfg_data["cores"][name].split(':')
            port = int(port)
            self.keystore.add_peer(PeerNode(ip, port, name, True), None)
        self.keystore.print_peer_keystore()


    def init_components(self) -> None:
        '''
        
        '''

    
    def start_threads(self) -> None:
        '''
        
        '''

# ======================================================================================================================
if __name__ == "__main__":
    n = Node("./cfg")
