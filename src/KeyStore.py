import Messages
from Messages import Packet
from PeerNode import PeerNode

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from dataclasses import dataclass
from struct import pack, unpack
from typing import Dict, Union


# ======================================================================================================================
@dataclass
class KeyPair:
    '''Basic class for storing PKI key pairs.

    Attributes:
        public (rsa.RSAPublicKey): Public key for encryption.
        private (rsa.RSAPrivateKey): Private key for decryption.
    
    '''
    public:  rsa.RSAPublicKey  = None
    private: rsa.RSAPrivateKey = None



# ======================================================================================================================
class KeyStore(object):
    '''Object designated to store all public and private keys for a session.

    Attributes:
        server_keypair (KeyPair): Key pair containing the public and private keys of the server component.
        client_keypair (KeyPair): Key pair containing the public and private keys of the client component.
        peer_public_keys (Dict[PeerNode, rsa.RSAPublicKey]): Peer nodes and their associated public key.
    
    Note:
        A dictionary is used for the Peer-Key pairings so a peer is not included twice.
    
    '''
    def __init__(self) -> None:
        '''Initializer for KeyStore class. Instantiates empty member data.
        
        '''
        self.server_keypair:   KeyPair                          = KeyPair()
        self.client_keypair:   KeyPair                          = KeyPair()
        self.peer_public_keys: Dict[PeerNode, rsa.RSAPublicKey] = dict()

    
    def load_server_keys(self, public_key: str, private_key: str) -> None:
        '''Load the public and private keys associated with the server.

        Parameters:
            public_key (str): Path to the file containing the public key of the server.
            private_key (str): Path to the file containing the private key of the server.
        
        '''
        with open(public_key, "rb") as key_read:
            self.server_keypair.public = serialization.load_pem_public_key(key_read.read(),
                                                                           backend=default_backend())
        with open(private_key, "rb") as key_read:
            self.server_keypair.private = serialization.load_pem_private_key(key_read.read(),
                                                                             password=None,
                                                                             backend=default_backend())
            
    
    def load_client_keys(self, public_key: str, private_key: str) -> None:
        '''Load the public and private keys for the client.

        Parameters:
            public_key (str): Path to the file containing the public key for the client.
            private_key (str): Path to the file containing the private key for the client.
        
        '''
        # Load pem keys from files
        with open(public_key, "rb") as key_read:
            self.client_keypair.public = serialization.load_pem_public_key(key_read.read(),
                                                                           backend=default_backend())
        with open(private_key, "rb") as key_read:
            self.client_keypair.private = serialization.load_pem_private_key(key_read.read(),
                                                                             password=None,
                                                                             backend=default_backend())
            
    
    def add_peer(self, peer: PeerNode, key: Union[rsa.RSAPublicKey, None]) -> None:
        '''Add a new peer and their public key to the keystore.

        Parameters:
            peer (PeerNode.PeerNode): Data about the new peer being added.
            key (None | rsa.RSAPublicKey): Contains either the public key of the peer being added to
                                           the list or None when that information is not yet known.
        
        '''
        self.peer_public_keys[peer] = key


    def set_peer_key(self, peer: PeerNode, key: Union[bytes, rsa.RSAPublicKey]) -> None:
        '''Sets the public key for a given peer.

        Parameters:
            peer (PeerNode.PeerNode): Desired node to have the key associated with.
            key (bytes | rsa.RSAPublicKey): The public key to be associated with the host specified.
                                            If the parameter is of type `bytes`, then it will be
                                            converted into `rsa.RSAPublicKey`.
        
        '''
        if(type(key) is bytes):
            key = serialization.load_pem_public_key(key, backend=default_backend())
        self.peer_public_keys[peer] = key


    def print_peer_keystore(self) -> None:
        '''Prints information about all of the peers in a keystore.
        
        '''
        for peer in self.peer_public_keys.keys():
            print(str(peer) + " - " + str(self.peer_public_keys[peer]))

    
    def get_peer(self, p: PeerNode) -> Union[PeerNode, None]:
        '''Finds a `PeerNode` in the Peer-Public Key dictionary with the same IP address and port as
           the one provided.

        Parameters:
            p (PeerNode.PeerNode): `PeerNode` initialized with an IP and port to be searched for in
                                   the keystore's database.
        
        Returns:
            An instance of `PeerNode` if the desired IP and port were found, and `None` if the
            keystore doesn't have any relevant peers.
        
        '''
        for peer in self.peer_public_keys.keys():
            if(p == peer):
                return peer
        return None
    

    def get_pub_key(self, p: PeerNode) -> Union[rsa.RSAPublicKey, None]:
        '''
        
        '''
        try:
            return(self.peer_public_keys[p])
        except KeyError as ke:
            return None



    def gen_keys(self, public_key: str, private_key: str) -> None:
        '''Generates a private key and its derived public key and stores the pair in seperate files.

        Parameters:
            public_key (str): The file path the public key's data will be written to.
            private_key (str): The file path the private key's data will be written to.
        
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


    def encrypt_packet(self, packet: Packet, peer: PeerNode) -> bytes:
        '''Encrypts a packet's contents using a public key stored in the keystore.

        Parameters:
            packet (Messages.Packet): Packet containing data to be encrypted.
            peer (PeerNode.PeerNode): Peer whose public key will be used for encryption.

        Returns:
            A `Packet` with the body containing the encrypted preamble and body of the original packet.
        '''
        pub_key = self.get_pub_key(peer)
        byte_string = packet.pack()
        enc_string = pub_key.encrypt(byte_string, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                               algorithm=hashes.SHA256(),
                                                               label=None))
        return enc_string



        

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
    raise(NotImplementedError("KeyStore is not designed to be ran as a stand-alone object"))
