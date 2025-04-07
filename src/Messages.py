from dataclasses import dataclass
from enum import Enum

# Standardized message strings for networked communication
# Messages where only the preamble is used and the body ignored
class PreambleOnly(Enum):
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
    MSG_ECHO  = 1 # Instruct receiver to echo back message
    MSG_ISKEY = 2 # Body data is a public key
    MSG_DATA  = 3 # Data is contained in the body


# Message contains multiple fields or packets
class MultiPacket(Enum):
    MSG_FORWARD = 1 # Node should decrypt body and forward it
    MSG_STOP    = 2 # Node is intended destination


# DEBUG messages
class DebugMessage(Enum):
    MSG_SHUTDOWN = 1 # Instruct remote server to shutdown


# Connection-related messages
MSG_HELLO = "HELLO".encode("utf-8") # Only ever issued by a client upon initial connection
MSG_BLOCK = "BLOCK".encode("utf-8") # Connection attempt has been blocked
MSG_EXIT  = "EXIT".encode("utf-8")  # Connection should close

# Operation messages
MSG_ECHO   = "ECHO".encode("utf-8")   # Have server send back message
MSG_GETKEY = "GETKEY".encode("utf-8") # Request to obtain key
MSG_ISKEY  = "ISKEY".encode("utf-8")  # Rest of message contains key
MSG_DENY   = "DENY".encode("utf-8")   # Request has been denied
MSG_OKAY   = "OKAY".encode("utf-8")   # Data sent was received

# Data transmission messages
MSG_DATA    = "DATA".encode("utf-8")    # Data follows this transmission
MSG_FORWARD = "FORWARD".encode("utf-8") # Forward data to next node
MSG_STOP    = "STOP".encode("utf-8")    # Destination has been reached

# Utility messages
MSG_NULLSTR = "".encode("utf-8")    # Returned by crashed clients
MSG_UNKNOWN = "???".encode("utf-8") # Unknown message response

# DEBUG messages
MSG_DBG_SHUTDOWN = "DBG_SHUTDOWN".encode("utf-8") # Instruct remote server to shutdown


@dataclass
class Packet:
    '''Dataclass used to handle packet formatting.

    Attributes:
        _preamble (bytes): The operation to be performed on the body data.
        _body (bytes): The primary data body containing all information, if any.

    '''
    _preamble: bytes = bytes()
    _body:     bytes = bytes()

    def construct(self, preamble: int, body: bytes | str) -> None:
        '''Changes the internal variables of the instance.

        Attributes:
            preamble (int): Message type to be stored in the preamble.
            body (bytes | str): Data associated with the message type.
        
        '''
        self._preamble = bytes([preamble])
        if(type(body) == str):
            body = body.encode("utf-8")
        self._body = body
        

    def pack(self) -> bytes:
        '''Pack everything in the class into a single bytes object.

        Returns:
            The preamble concatenated with the body of the calling class instance.
        
        '''
        return(self._preamble + self._body)

