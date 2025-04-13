import argparse
from enum import Enum, auto
import socket
from struct import pack, unpack

class PacketType(Enum):
    CONNECT    = auto()
    DISCONNECT = auto()
    MESSAGE    = auto()


# Network info
PORT = 7877
PACKET_FORMAT = "!9sHH"

# Target cores
CORE_A: str = ""
CORE_B: str = ""
CORE_C: str = ""
CORE_LIST = [CORE_A, CORE_B, CORE_C]
DEST:   str = ""


def route_core() -> None:
    '''
    
    '''
    



def run_server() -> None:
    '''
    
    '''
    # Server Socket connection
    serve_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serve_sock.bind(('', PORT))
    # Running the server
    run_server = True
    while run_server:
        serve_sock.listen(5)
        conn, conn_info = serve_sock.accept()




# ======================================================================================================================
def create_argv() -> argparse.Namespace:
    '''Parse the command line arguments passed in with the program.

    Returns:
        A namespace through which arguments can be accessed.
    
    '''
    parser = argparse.ArgumentParser(prog="Arbitrary Network",
                                     description="Arbitrary anonymization network",)
    parser.add_argument("-p", "--port",
                        help="Port override for server",
                        type=int,)
    parser.add_argument("-m", "--mode",
                        help="Mode override",
                        type=str,
                        choices=["client", "server"],
                        default="relay")
    return parser.parse_args()


# ======================================================================================================================
if __name__ == "__main__":
    pass
