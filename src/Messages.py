from dataclasses import dataclass
from enum import Enum
from struct import pack, unpack

# Standardized message strings for networked communication
# Messages where only the preamble is used and the body ignored
class PreambleOnly(Enum):
    MSG_NONE    = 0 # Packet is not associated with a message
    MSG_HELLO   = 1 # Only ever issued by a client upon initial connection
    MSG_BLOCK   = 2 # Connection attempt has been blocked
    MSG_OKAY    = 3 # Last message sent was received
    MSG_EXIT    = 4 # Connection is being closed by other endpoint
    MSG_GETKEY  = 5 # Request to obtain receiver's public key
    MSG_DENY    = 6 # Request has been denied by server
    # Utility
    MSG_NULLSTR = 7 # Null string, often sent by crashed clients
    MSG_UNKNOWN = 8 # Server could not interpret provided message


# Messages where the body contains additional information
class BodyData(Enum):
    MSG_ECHO  =  9 # Instruct receiver to echo back message
    MSG_ISKEY = 10 # Body data is a public key
    MSG_DATA  = 11 # Data is contained in the body


# Message contains multiple fields or packets
class MultiPacket(Enum):
    MSG_FORWARD = 12 # Node should decrypt body and forward it
    MSG_STOP    = 13 # Node is intended destination


# DEBUG messages
class DebugMessage(Enum):
    MSG_SHUTDOWN = 100 # Instruct remote server to shutdown



@dataclass
class Packet:
    '''Dataclass used to handle packet formatting.

    Attributes:
        _preamble (bytes): The operation to be performed on the body data.
        _body (bytes): The primary data body containing all information, if any.

    '''
    _preamble: int   = PreambleOnly.MSG_NONE
    _body:     bytes = bytes()


    def construct(self, preamble: Enum | int, body: bytes | str) -> None:
        '''Changes the internal variables of the instance.

        Parameters:
            preamble (Enum | int): Message type to be stored in the preamble.
            body (bytes | str): Data associated with the message type.
        
        '''
        self.preamble = preamble
        self.body = body
        

    def pack(self) -> bytes:
        '''Pack everything in the class into a single bytes object.

        Returns:
            The preamble concatenated with the body of the calling class instance.
        
        '''
        return(pack("!H2046s", self._preamble, self._body))
    

    def unpack(self, packet: bytes) -> None:
        '''Converts packed byte sequence into a readable packet.

        Parameters:
            packet (bytes): Raw byte sequence to be unpacked into Packet object.
        
        '''
        preamble, body = unpack("!H2046s", packet)
        self.construct(preamble, body)


    @property
    def preamble(self) -> int:
        return self._preamble
    

    @preamble.setter
    def preamble(self, p: Enum | int) -> None:
        if(isinstance(p, Enum)):
            p = int(p.value)
        self._preamble = p


    @property
    def body(self) -> str:
        return self._body.decode("utf-8")
    

    @body.setter
    def body(self, b: bytes | str) -> None:
        if(isinstance(b, str)):
            b = b.encode("utf-8")
        self._body = b

    
    def __str__(self) -> str:
        return(f"[{self.preamble}, {self.body}]")

