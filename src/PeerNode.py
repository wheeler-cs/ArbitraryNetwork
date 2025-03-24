from dataclasses import dataclass


@dataclass
class PeerNode:
    '''
    
    '''
    ip: str
    port: str
    name: str = "UNDEFINED"
    public_key: str = ""

