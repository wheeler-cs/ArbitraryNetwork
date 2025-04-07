from PeerNode import PeerNode

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from dataclasses import dataclass
from typing import Dict


# ======================================================================================================================
@dataclass
class KeyPair:
    public: rsa.RSAPublicKey   = None
    private: rsa.RSAPrivateKey = None



# ======================================================================================================================
class KeyStore(object):
    '''
    
    '''
    def __init__(self) -> None:
        '''
        
        '''
        self.server_keypair:   KeyPair                          = KeyPair()
        self.client_keypair:   KeyPair                          = KeyPair()
        self.peer_public_keys: Dict[PeerNode, rsa.RSAPublicKey] = dict()

    
    def load_server_keys(self, public_key: str, private_key: str) -> None:
        '''
        
        '''
        with open(public_key, "rb") as key_read:
            self.server_keypair.public = serialization.load_pem_public_key(key_read.read(),
                                                                           backend=default_backend())
        with open(private_key, "rb") as key_read:
            self.server_keypair.private = serialization.load_pem_private_key(key_read.read(),
                                                                             password=None,
                                                                             backend=default_backend())
            
    
    def load_client_keys(self, public_key: str, private_key: str) -> None:
        '''
        
        '''
        # Load pem keys from files
        with open(public_key, "rb") as key_read:
            self.client_keypair.public = serialization.load_pem_public_key(key_read.read(),
                                                                           backend=default_backend())
        with open(private_key, "rb") as key_read:
            self.client_keypair.private = serialization.load_pem_private_key(key_read.read(),
                                                                             password=None,
                                                                             backend=default_backend())
            
    
    def add_peer(self, peer: PeerNode, key: None | rsa.RSAPublicKey) -> None:
        '''
        
        '''
        self.peer_public_keys[peer] = key


    def set_peer_key(self, peer: PeerNode, key: bytes | rsa.RSAPublicKey) -> None:
        '''
        
        '''
        print(type(key))
        if(type(key) is bytes):
            key = serialization.load_pem_public_key(key, backend=default_backend())
        self.peer_public_keys[peer] = key


    def print_peer_keystore(self) -> None:
        '''
        
        '''
        for peer in self.peer_public_keys:
            print(str(peer) + " - " + str(self.peer_public_keys[peer]))


    def gen_keys(self, public_key:str, private_key: str) -> None:
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
        with open(private_key, "wb") as key_write:
            key_write.write(pem_priv)
        with open(public_key, "wb") as key_write:
            key_write.write(pem_pub)
        

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



# ======================================================================================================================
if __name__ == "__main__":
    print("[ERR] Cannot run KeyStore as standalone instance")
