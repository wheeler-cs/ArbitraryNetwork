from KeyStore import KeyStore
from Messages import *
from PeerNode import PeerNode

import json
import socket
from typing import List, Set



# ======================================================================================================================
class Client(object):
    '''
    
    '''

    def __init__(self, cfg_file: str = "cfg/client.json") -> None:
        '''
        
        '''
        # Connection information
        self.peers: List[PeerNode] = list()
        self.connections: dict[str, socket.socket] = dict()
        self.min_reroute_timeout: int = Configuration.DEFAULT_MIN_REROUTE_TIMEOUT
        self.max_reroute_timeout: int = Configuration.DEFAULT_MAX_REROUTE_TIMEOUT
        # Key information
        self.keystore: KeyStore = None
        # Setup client
        self.load_cfg(cfg_file)
        self.init_core()
    

    def load_cfg(self, cfg_file: str = "cfg/client.json") -> None:
        '''
        
        '''
        cfg_data = None
        with open(cfg_file, 'r') as cfg_read:
            cfg_data = json.load(cfg_read)
        self.keystore = KeyStore(cfg_data["files"]["public_key"], cfg_data["files"]["private_key"])
        for peer_name in cfg_data["cores"]:
            contact_str = cfg_data["cores"][peer_name]
            ip, port = contact_str.split(':')
            port = int(port)
            self.peers.append(PeerNode(ip, port, name=peer_name, is_core=True))

    
    def init_core(self) -> None:
        '''
        
        '''
        peers_connected = 0
        for peer in self.peers:
            self.connect(peer)
            if(peer.conn is not None):
                self.get_key(peer)
                peers_connected += 1
        print(f"[INFO] Loaded {peers_connected}/{len(self.peers)} peer keys")
    

    def connect(self, peer: PeerNode) -> None:
        '''Attempt outgoing connection to external server.

        Args:
            ip (str): IPv4 address of target server.
            port (int): Port server is listening for connections on.
        '''
        try:
            if(peer.conn is None):
                new_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_conn.connect((peer.ip, peer.port))
                response = new_conn.recv(2048)
                if(response == MSG_HELLO):
                    print(f"[INFO] Connected with {peer.ip} on {peer.port}")
                    peer.conn = new_conn
                elif(response == MSG_BLOCK):
                    print(f"[WARN] Peer {peer.ip} on {peer.port} has issued a block")
                    new_conn.close()
                else:
                    raise Exception("Peer did not respond to connection")
        except Exception as e:
            print(f"[ERR] Unable to establish forward connection with {peer.ip} on {peer.port}\n |-> {e}")
            if(new_conn is not None):
                new_conn.close()
    

    def get_key(self, peer: PeerNode) -> None:
        '''
        
        '''
        peer.conn.send(MSG_GETKEY)
        response = peer.conn.recv(2048)
        # Check for specific errors
        if(response == MSG_DENY):
            print(f"[WARN] Peer {peer.ip} on {peer.port} denied key request")
        # Parse message
        response = response.decode("utf-8")
        if(response[:5].encode() == MSG_ISKEY):
            peer.public_key = ''.join(response.split('\n')[1:-2])
            print(peer.public_key)
        else:
            print(f"[ERR] Server sent back unknown message: {response}")
        

    
    def disconnect(self, ip: str) -> None:
        '''Close outgoing connection with server.

        Args:
            ip (str): IPv4 address of connection to be closed.
        
        '''
        try:
            for peer in self.peers:
                if(peer.ip == ip):
                    peer.conn.close()
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
            data = data.encode("utf-8")
        for peer in self.peers:
            if(peer.ip == ip):
                peer.conn.send(data)
                break

    
    def recv(self, ip: str) -> bytes:
        '''Receive data from a specific connection.

        Args:
            ip (str): IPv4 address client anticipates data from.
        
        '''
        data = b''
        for peer in self.peers:
            if(peer.ip == ip):
                data = peer.conn.recv(2048)
                break
        return data

    
    def console_mode(self, ip: str) -> None:
        '''Enter console mode for string-based entry of data.

        Args:
            ip (str): IPv4 address to send and receive data over.
        
        '''
        msg = ''
        while True:
            msg = input("> ")
            if(msg != ''):
                self.send(ip, msg.encode("utf-8"))
                response = self.recv(ip)
                print(response.decode("utf-8"))
                if(response == MSG_EXIT):
                    break



# ======================================================================================================================
if __name__ == "__main__":
    print("[Running Stand-Alone Client]")
    client = Client()
    client.console_mode("127.0.0.1")
    client.disconnect("127.0.0.1")
    