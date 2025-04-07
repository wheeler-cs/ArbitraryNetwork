from dataclasses import dataclass

# Standardized message strings for networked communication

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

    def construct(self, preamble: bytes | str, body: bytes) -> None:
        '''Changes the internal variables of the instance.

        Attributes:
            preamble (bytes | str): Message to be stored in the preamble.
            body (bytes): Body containing any needed data.
        
        '''
        if(type(preamble) is str):
            preamble = preamble.encode("utf-8")
        self._preamble = preamble
        self._body = body
        

    def pack(self) -> bytes:
        '''Pack everything in the class into a single bytes object.

        Returns:
            The preamble concatenated with the body of the calling class instance.
        
        '''
        return(self._preamble + self._body)

