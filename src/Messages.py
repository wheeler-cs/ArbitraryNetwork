from dataclasses import dataclass
from enum import Enum, auto
from struct import pack, unpack
from typing import Union


'''
I hate how Python implements enums...
'''

# Standardized message strings for networked communication
class Preambles(Enum):
    '''Packets of this type ignore all data stored in the body portion.
    
    '''
    MSG_NONE     = auto() # Packet is not associated with a message
    # Connection handling
    MSG_HELLO    = auto() # Only ever issued by a client upon initial connection
    MSG_CONN_REQ = auto() # Message is a connection request; sent to destination node
    MSG_BLOCK    = auto() # Connection attempt has been blocked
    MSG_OKAY     = auto() # Last message sent was received
    MSG_EXIT     = auto() # Connection is being closed by other endpoint
    # Key exchanging
    MSG_GETKEY   = auto() # Request to obtain receiver's public key
    MSG_ISKEY    = auto() # Body data is a public key
    # Data processing
    MSG_DATA     = auto() # Data is contained in the body
    MSG_TEXT     = auto() # Data in the body is text data
    MSG_ENC      = auto() # Data is encrypted
    MSG_ISEND    = auto() # Receiver is the target for the data
    MSG_STOP     = auto() # Node is intended destination
    MSG_DENY     = auto() # Request has been denied by server
    MSG_PEERS    = auto() # Get a list of peers currently known by self
    MSG_FORWARD  = auto() # Node should decrypt body and forward it
    # Utility
    MSG_ECHO     = auto() # Instruct receiver to echo back message
    MSG_NULLSTR  = auto() # Null string, often sent by crashed clients
    MSG_UNKNOWN  = auto() # Server could not interpret provided message
    # Debugging
    MSG_SHUTDOWN = 100 # Instruct remote server to shutdown



@dataclass
class Packet:
    '''Dataclass used to handle packet formatting.

    Attributes:
        _preamble (bytes): The operation to be performed on the body data.
        _body (bytes): The primary data body containing all information, if any.

    '''
    _preamble:  int   = Preambles.MSG_NONE.value
    _dest_ip:   str   = "127.0.0.1"
    _dest_port: int   = 7877
    _data_size: int   = 0
    _body:      bytes = bytes()


    def construct(self, preamble: Enum | int, ip: str, port: int, size: int, body: bytes | str) -> None:
        '''Changes the internal variables of the instance.

        Parameters:
            preamble (Enum | int): Message type to be stored in the preamble.
            ip (str): IP address for the destination.
            port (int): Target port associated with the IP address.
            size (int): Size of the overall message.
            body (bytes | str): Data associated with the message type.
        
        '''
        self.preamble   = preamble
        self._dest_ip   = ip
        self._dest_port = port
        self._data_size = size
        self.body       = body


    def pack(self) -> bytes:
        '''Pack everything in the class into a single bytes object.

        Returns:
            The preamble concatenated with the body of the calling class instance.
        
        '''
        return(pack(f"!H9sHH{int(len(self._body))}s",
                    self._preamble,
                    self._dest_ip.encode("utf-8"),
                    self._dest_port,
                    self._data_size,
                    self._body))
    

    def unpack(self, packet: bytes) -> None:
        '''Converts packed byte sequence into a readable packet.

        Parameters:
            packet (bytes): Raw byte sequence to be unpacked into Packet object.
        
        '''
        preamble, ip, port, size, body = unpack(f"!H9sHH{len(packet)-15}s", packet)
        self.construct(preamble, ip, port, size, body)


    # Accessors and Mutators -----------------------------------------------------------------------
    @property
    def preamble(self) -> int:
        return self._preamble
    

    @preamble.setter
    def preamble(self, p: Union[Enum, int]) -> None:
        if(isinstance(p, Enum)):
            p = int(p.value)
        self._preamble = p


    @property
    def body(self) -> str:
        return self._body.decode("utf-8")
    

    @body.setter
    def body(self, b: Union[bytes, str]) -> None:
        if(isinstance(b, str)):
            b = b.encode("utf-8")
        self._body = b

    
    # Overrides ------------------------------------------------------------------------------------
    def __str__(self) -> str:
        return(f"[{self.preamble}, {self.body}]")

