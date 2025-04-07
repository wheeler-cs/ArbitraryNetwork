from dataclasses import dataclass
import socket

from cryptography.hazmat.primitives.asymmetric import rsa

# ======================================================================================================================
class PeerNode(object):
    '''Class used to maintain information about peer nodes.

    Attributes:
        _ip (str): IP address of associated node.
        _port (int): Target port server component is running on.
        _name (str): Customizable human-readable name for peer.
        _is_core (bool): Flag indicating if the node is a trusted core member.
    
    '''
    def __init__(self, ip: str = "", port: int = 8192, name: str = "UNDEFINED", is_core = False) -> None:
        self._ip:         str  = ip
        self._port:       str  = port
        self._name:       str  = name
        self._is_core:    bool = is_core


    # Accessors and mutators -----------------------------------------------------------------------
    @property
    def ip(self) -> str:
        return self._ip
    

    @ip.setter
    def ip(self, i: str) -> None:
        self._ip = i
    
    
    @property
    def port(self) -> int:
        return self._port


    @port.setter
    def port(self, p: int) -> None:
        self._port = p

    
    @property
    def name(self) -> str:
        return self._name
    

    @name.setter
    def name(self, n: str) -> None:
        self._name = n

    
    @property
    def is_core(self) -> bool:
        return self._is_core
    

    @is_core.setter
    def is_core(self, c: bool) -> None:
        self._is_core = c


    @property
    def socket_addr(self) -> str:
        return(self.ip + ':' + str(self.port))
    

    @socket_addr.setter
    def socket_addr(self, addr: str) -> None:
        try:
            ip, port = addr.split(':')
            port = int(port)
            self._ip = ip
            self._port = port
        except Exception as e:
            print("Socket address is not properly formatted")


    # Overrides ------------------------------------------------------------------------------------
    def __hash__(self):
        return(hash(self.socket_addr))


    def __eq__(self, other) -> bool:
        return((self.socket_addr == other.socket_addr))
    

    def __str__(self) -> str:
        return(("[C] " if self.is_core else "    ") + self.name + '@' + self.socket_addr)

