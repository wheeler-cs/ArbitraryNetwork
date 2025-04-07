from KeyStore import KeyStore
import Messages
from PeerNode import PeerNode

import argparse
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import json
from os import path
import socket
import threading
from time import sleep
from typing import Set


class Node(object):
    '''
    
    '''
    def __init__(self, cfg_dir: str, port: int | None = None, mode: str = "relay") -> None:
        '''
        
        '''
        # Functionality information
        self.mode:          str              = mode
        # Server variables
        self.server_port:   int              = port
        self.server_sock:   socket.socket    = None
        self.server_thread: threading.Thread = None
        # Client variables
        self.path_length:   int              = 0
        self.client_sock:   socket.socket    = None
        self.client_thread: threading.Thread = None
        # Cryptographic information
        self.keystore:      KeyStore         = KeyStore()
        # Initialization
        self.load_cfg(path.join(cfg_dir, "server.json"), path.join(cfg_dir, "client.json"))
        self.init_components()
        self.start_threads()


    def load_cfg(self, server_cfg: str, client_cfg: str) -> None:
        '''
        
        '''
        if((self.mode == "server") or (self.mode == "relay")):
            self.load_server_cfg(server_cfg)
        if((self.mode == "client") or (self.mode == "relay")):
            self.load_client_cfg(client_cfg)
    

    def load_server_cfg(self, cfg_file: str) -> None:
        '''
        
        '''
        cfg_data = None
        with open(cfg_file, 'r') as server_cfg:
            cfg_data = json.load(server_cfg)
        if(self.server_port is None): # Handle port override from argv
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
        if((self.mode == "server") or (self.mode == "relay")):
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.bind(('', self.server_port))
        # Initialize client
        if((self.mode == "client") or (self.mode == "relay")):
            self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def contact_core(self) -> None:
        '''
        
        '''
        for peer in self.keystore.peer_public_keys.keys():
            try:
                self.client_sock.connect((peer.ip, peer.port))
                self.client_sock.send(Messages.MSG_GETKEY)
                response = self.client_sock.recv(2048)
                if(response == Messages.MSG_BLOCK):
                    print("[CLIENT] Peer blocked request for key")
                    peer_key = None
                elif(response.decode("utf-8")[:5] == "ISKEY"):
                    # Need to get rid of "ISKEY" portion of packet and reencode
                    peer_key = (response.decode("utf-8")[5:]).encode("utf-8")
                self.client_sock.close()
                self.keystore.set_peer_key(PeerNode(ip=peer.ip, port=peer.port), peer_key)
            except Exception as e:
                print(f"[CLIENT] Unable to contact {peer.ip}:{peer.port} in core")
                print(f"         |-> {e}")
        self.keystore.print_peer_keystore()


    def connect(self, target: PeerNode) -> None:
        '''
        
        '''
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_sock.connect((target.ip, target.port))
            self.client_sock.send(Messages.MSG_HELLO)
        except Exception as e:
            print("[CLIENT] Unable to connect with server")
            print(f"        |-> {e}")

    
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
            elif(message == "SHUTDOWN"):
                self.client_sock.send(Messages.MSG_DBG_SHUTDOWN)
                self.client_sock.close()
                do_terminal = False
            elif("ECHO" in message):
                self.client_sock.send(message.encode("utf-8"))
                response = self.client_sock.recv(2048)
                print(f"[CLIENT] Server Echo: {response.decode('utf-8')}")
            else:
                self.client_sock.send(message.encode("utf-8"))
                response = self.client_sock.recv(2048)
                print(f"[CLIENT] Server Responded: {response.decode('utf-8')}")
    
    
    def start_threads(self) -> None:
        '''
        
        '''
        if(self.mode == "server"):
            self.run_server()
        elif(self.mode == "client"):
            self.contact_core()
            self.connect(PeerNode(ip="127.0.0.1", port=7877))
            self.client_as_terminal()
        else:
            self.server_thread = threading.Thread(target=self.run_server)
            self.server_thread.start()
            sleep(2) # Gives server thread time to start before cores on the same host contact it
            self.contact_core()
            self.connect(PeerNode(ip="127.0.0.1", port=7877))
            self.client_as_terminal()
            self.server_thread.join()


    def run_server(self) -> None:
        '''
        
        '''
        print(f"[SERVER] Running on port {self.server_port}")
        do_server = True
        # Run server process
        while do_server:
            self.server_sock.listen(5)
            conn, addr = self.server_sock.accept()
            message = conn.recv(2048)
            # NOTE: GETKEY closes connection immediately after sending key
            if(message == Messages.MSG_GETKEY):
                response = Messages.MSG_ISKEY + self.keystore.server_keypair.public.public_bytes(encoding=serialization.Encoding.PEM,
                                                                                                 format=serialization.PublicFormat.SubjectPublicKeyInfo)
                conn.send(response)
                conn.close()
            # NOTE: HELLO starts a new client dialog
            elif(message == Messages.MSG_HELLO):
                print(f"[SERVER] Received connection from {addr}")
                do_conn = True
                # Run an active connection with client
                while do_conn:
                    message = conn.recv(2048)
                    print(f"[SERVER] {addr}: {message.decode('utf-8')}")
                    if(Messages.MSG_ECHO.decode("utf-8") == message.decode("utf-8")[:4]): # Echo message to client
                        conn.send(message)
                    elif(message == Messages.MSG_EXIT): # Client is disconnecting
                        do_conn = False
                    elif(message == Messages.MSG_DBG_SHUTDOWN): # DEBUG: Shutdown server using client
                        do_conn = False
                        do_server = False
                    else: # Message could not be interpreted
                        conn.send(Messages.MSG_UNKNOWN)
                conn.close()
        print(f"[SERVER] Terminating operation")


# ======================================================================================================================
def create_argv() -> argparse.Namespace:
    '''
    
    '''
    parser = argparse.ArgumentParser(prog="Arbitrary Network",
                                     description="Arbitrary anonymization network",)
    parser.add_argument("--cfg_dir",
                        help="Directory containing configuration files",
                        type=str,
                        default="./cfg")
    parser.add_argument("-p", "--port",
                        help="Port override for server",
                        type=int,)
    parser.add_argument("-m", "--mode",
                        help="Mode override",
                        type=str,
                        choices=["server", "client", "relay"],
                        default="relay")
    return parser.parse_args()


# ======================================================================================================================
if __name__ == "__main__":
    argv = create_argv()
    n = Node(argv.cfg_dir, argv.port, argv.mode)
