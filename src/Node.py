from KeyStore import KeyStore
import Messages
from PeerNode import PeerNode

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
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
        self.server_port = int(cfg_data["connection"]["port"])
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


    def init_components(self) -> None:
        '''
        
        '''
        # Initialize server
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind(('', self.server_port))


    def contact_core(self) -> None:
        '''
        
        '''
        for peer in self.keystore.peer_public_keys.keys():
            self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_sock.connect((peer.ip, peer.port))
            self.client_sock.send(Messages.MSG_GETKEY)
            response = self.client_sock.recv(2048)
            if(response == Messages.MSG_BLOCK):
                print("[WARN] Peer blocked request for key")
            elif(response.decode("utf-8")[:5] == "ISKEY"):
                peer_key = response.decode()[5:]
                print(peer_key)

    
    def client_as_terminal(self) -> None:
        '''
        
        '''
        do_terminal = True
        while do_terminal:
            message = input("> ")
            if(message == "EXIT"):
                self.client_sock.send(Messages.MSG_EXIT)
                self.client_sock.close()
                do_terminal = False
            elif("ECHO" in message):
                self.client_sock.send(message.encode("utf-8"))
            response = self.client_sock.recv(2048)
            print(f"[CLIENT] {response.decode('utf-8')}")
    
    
    def start_threads(self) -> None:
        '''
        
        '''
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.start()
        self.contact_core()
        self.client_as_terminal()
        self.server_thread.join()


    def run_server(self) -> None:
        '''
        
        '''
        while True:
            self.server_sock.listen(5)
            conn, addr = self.server_sock.accept()
            message = conn.recv(2048)
            if(message == Messages.MSG_GETKEY):
                response = Messages.MSG_ISKEY + self.keystore.server_keypair.public.public_bytes(encoding=serialization.Encoding.PEM,
                                                                                                 format=serialization.PublicFormat.SubjectPublicKeyInfo)
                conn.send(response)
                conn.close()
            else:
                do_conn = True
                #conn.send(Messages.MSG_HELLO)
                while do_conn:
                    message = conn.recv(2048)
                    print(f"[SERVER] {message.decode('utf-8')}")
                    if(Messages.MSG_ECHO.decode("utf-8") == message.decode()[:4]):
                        conn.send(message)
                    elif(message == Messages.MSG_EXIT):
                        do_conn = False
                    else:
                        conn.send(Messages.MSG_UNKNOWN)
                conn.close()




# ======================================================================================================================
if __name__ == "__main__":
    n = Node("./cfg")
