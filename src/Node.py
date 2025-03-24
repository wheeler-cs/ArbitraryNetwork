from Client import Client
from PeerNode import PeerNode
from Server import Server

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import json
from typing import List


class Node(object):
    '''

    Code for handling keys adapted from https://nitratine.net/blog/post/asymmetric-encryption-and-decryption-in-python/
    
    '''
    def __init__(self, cfg_file: str = "cfg/core.json") -> None:
        '''
        
        '''
        # Member variables
        self.core:        List[PeerNode] = list()
        self.peers:       List[PeerNode] = list()
        self.path:        List[PeerNode] = list()
        self.public_key:  rsa            = ""
        self.private_key: rsa            = ""
        # Networking infrastructure
        self.client: Client = Client()
        self.server: Server = Server()
        # Setup
        self.load_cfg(cfg_file)

    
    def load_cfg(self, cfg_file: str) -> None:
        '''
        
        '''
        cfg_data = None
        with open(cfg_file, 'r') as cfg_read:
            cfg_data = json.load(cfg_read)
        # Load data about core nodes
        for idx, member in enumerate(cfg_data["core_members"]):
            node_name = member
            ip_port = cfg_data["core_members"][member]
            ip, port = ip_port.split(':')
            new_peer = PeerNode(ip, port, node_name)
            self.core.append(new_peer)
        self.peers = self.core.copy()
    

    def gen_keys(self, key_schema: str = "keys/key") -> None:
        '''
        
        '''
        # Create keys
        priv = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        pub = priv.public_key()
        # Convert keys to pems
        pem_priv = priv.private_bytes(encoding=serialization.Encoding.PEM,
                                      format=serialization.PrivateFormat.PKCS8,
                                      encryption_algorithm=serialization.NoEncryption())
        pem_pub = pub.public_bytes(encoding=serialization.Encoding.PEM,
                                   format=serialization.PublicFormat.SubjectPublicKeyInfo)
        # Write pem data to files
        with open(key_schema + ".priv", "wb") as key_write:
            key_write.write(pem_priv)
        with open(key_schema + ".pub", "wb") as key_write:
            key_write.write(pem_pub)

        
    def load_keys(self, public_key: str, private_key: str) -> None:
        '''
        
        '''
        try:
            # Load pem keys from files
            with open(public_key, "rb") as key_read:
                self.public_key = serialization.load_pem_public_key(key_read.read(), backend=default_backend())
            with open(private_key, "rb") as key_read:
                self.private_key = serialization.load_pem_private_key(key_read.read(),
                                                                      password=None,
                                                                      backend=default_backend())
        except Exception as e:
            raise Exception("[ERR] Unable to load keys\n|-> Reason: {e}")
        

    def encrypt(self, data: bytes, key) -> bytes:
        '''
        
        '''
        enc_data = key.encrypt(data, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                  algorithm=hashes.SHA256(),
                                                  label=None))
        return enc_data


    def decrypt(self, data: bytes, key) -> bytes:
        '''
        
        '''
        dec_data = key.decrypt(data,
                               padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                            algorithm=hashes.SHA256(),
                                            label=None))
        return dec_data
    

    def connect_core(self) -> None:
        '''
        
        '''
        for idx, member in self.peers:
            self.get_peer_key(member.ip, member.port)
    

    def get_peer_key(self, ip: str, port: str) -> None:
        '''
        
        '''
        # Contact peer for key
        self.client.connect(ip, port)
        self.client.send(ip, b"GETKEY")
        response = self.client.recv(ip).decode()
        # Decode what response means
        if response == "BLOCK":
            print("[WARN] Node {ip} has blocked your key request")
        elif "ISKEY " == response[:6]:
            for idx, peer in enumerate(self.peers):
                if peer.ip == ip:
                    peer.public_key = response[5:]
    

    def run_server(self) -> None:
        '''
        
        '''
        self.server.run()



# ======================================================================================================================
if __name__ == "__main__":
    node = Node()
    node.load_keys("keys/key.pub", "keys/key.priv")
    enc_data = node.encrypt(b"Hello", node.public_key)
    print(len(enc_data))
