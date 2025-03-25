from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric import rsa


@dataclass
class PeerNode:
    '''Data class containing information needed to track associate nodes.
    
    '''
    ip:         str
    port:       str
    name:       str              = "UNDEFINED"
    public_key: rsa.RSAPublicKey = None
    is_core:    bool             = False

