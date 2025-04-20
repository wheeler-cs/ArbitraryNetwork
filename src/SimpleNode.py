import argparse
from enum import Enum, auto
import json
import socket
from struct import pack, unpack
from typing import Tuple

class PacketType(Enum):
    CONNECT    = auto()
    DISCONNECT = auto()
    MESSAGE    = auto()


# Network info
PORT = 7877
PACKET_FORMAT = "!256sHH64s"

CORE_A = ()
CORE_B = ()
CORE_C = ()
DEST   = ()


def load_cfg(cfg_file: str) -> None:
    '''
    
    '''
    with open(cfg_file, 'r') as parameters:
        data = json.load(parameters)
    hops = data["route"]
    global CORE_A
    global CORE_B
    global CORE_C
    global DEST
    CORE_A = (hops["HOP_A"], 7877)
    CORE_B = (hops["HOP_B"], 7877)
    CORE_C = (hops["HOP_C"], 7877)
    DEST   = (hops["HOP_D"], 7877)


def pack_packet(ip: str, port: int, packet_type: int, message: str) -> bytes:
    '''
    
    '''
    return pack(PACKET_FORMAT, ip.encode("ascii"), port, packet_type, message.encode("ascii"))


def unpack_packet(data: bytes) -> Tuple[str, int, int, str]:
    '''
    
    '''
    return unpack(PACKET_FORMAT, data)


def run_client() -> None:
    '''
    
    '''
    print("[CLIENT] Client running")
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((CORE_A))
    client_sock.send(pack_packet(CORE_B[0], CORE_B[1], PacketType.CONNECT.value, ''))
    client_sock.recv(1024)
    client_sock.send(pack_packet(CORE_C[0], CORE_C[1], PacketType.CONNECT.value, ''))
    client_sock.recv(1024)
    client_sock.send(pack_packet(DEST[0], DEST[1], PacketType.CONNECT.value, ''))
    client_sock.recv(1024)
    client_sock.send(pack_packet(DEST[0], DEST[1], PacketType.MESSAGE.value, "Hello, world!"))
    client_sock.recv(1024)
    client_sock.send(pack_packet(DEST[0], DEST[1], PacketType.DISCONNECT.value, ''))
    client_sock.recv(1024)
    client_sock.close()



def run_server(port: int) -> None:
    '''
    
    '''
    # Socket connections
    serve_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serve_sock.bind(('', port))
    # Running the server
    run_server = True
    while run_server:
        print("[SERVER] Server running")
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_active = False
        serve_sock.listen(5)
        conn, conn_info = serve_sock.accept()
        do_conn = True
        while do_conn:
            data = conn.recv(1024)
            print(f"Data Size: {len(data)}")
            ip, port, packet_type, message = unpack_packet(data)
            ip = ip.decode("ascii")
            message = message.decode("ascii")
            print(f"[PACKET] {PacketType(packet_type)}: {message}")
            conn.send(data)
            if(packet_type == PacketType.CONNECT.value):
                if(client_active):
                    print(f"[INTERMEDIATE] Forwarding packet: {ip}")
                    client_sock.send(data)
                    client_sock.recv(1024)
                else:
                    print(f"[CONNECTION] New connection: {ip}")
                    client_sock.connect((ip, port))
                    client_active = True
            elif(packet_type == PacketType.MESSAGE.value):
                if(client_active):
                    client_sock.send(data)
                    client_sock.recv(1024)
                else:
                    print(f"[END POINT] Message received: {message}")
            elif(packet_type == PacketType.DISCONNECT.value):
                if(client_active):
                    print(f"[DISCONNECT] Closing forward: {ip}")
                    client_sock.send(data)
                    client_sock.recv(1024)
                    client_sock.close()
                    client_active = False
                conn.close()
                do_conn = False
            else:
                pass






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
                        type=int,
                        default=7877)
    parser.add_argument("-m", "--mode",
                        help="Mode override",
                        type=str,
                        choices=["client", "server"],
                        default="server")
    return parser.parse_args()


# ======================================================================================================================
if __name__ == "__main__":
    argv = create_argv()
    if(argv.mode == "server"):
        run_server(argv.port)
    elif(argv.mode == "client"):
        load_cfg("cfg/client.json")
        run_client()
