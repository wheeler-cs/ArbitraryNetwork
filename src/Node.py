from KeyStore import KeyStore
import Messages
from PeerNode import PeerNode

import argparse
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import json
from os import path
import random
import socket
import threading
from time import sleep
from typing import List, Union


class Node(object):
    '''Node class that enables bi-directional communication with remote hosts.

    Attributes:
        mode (str): The mode of operation in which the instance should be ran. Will normally be set
                    to "relay" most of the time.
        route (list[PeerNode.PeerNode]): The route the client component will use when sending data
                                         to the desired destination.
        server_port (int): The port at which the server component can be reached.
        server_sock (socket.socket): The socket object for the server through which network data is
                                     passed.
        server_thread (threading.Thread): Secondary thread the server component will run on
                                          separately from the client.
        client_socket (socket.socket): Socket object over which client will send outgoing data.
        client_thread (threading.Thread): Secondary thread the client will run on separately from
                                          the server.
        keystore (Keystore.Keystore): Keystore object holding all public keys of peers and private
                                      keys of server and client components.
    
    '''
    def __init__(self, cfg_dir: str, port: Union[int, None] = None, mode: str = "relay") -> None:
        '''
        
        '''
        # Functionality information
        self.mode:          str              = mode
        self.route:         List[PeerNode]   = list()
        # Server variables
        self.server_port:   int              = port
        self.server_sock:   socket.socket    = None
        self.server_thread: threading.Thread = None
        # Client variables
        self.client_sock:   socket.socket    = None
        self.client_thread: threading.Thread = None
        # Cryptographic information
        self.keystore:      KeyStore         = KeyStore()
        # Initialization
        self.load_cfg(path.join(cfg_dir, "server.json"), path.join(cfg_dir, "client.json"))
        self.init_components()
        self.start_threads()


    def load_cfg(self, server_cfg: str, client_cfg: str) -> None:
        '''Load configuration data for server and client from files.

        Parameters:
            server_cfg (str): File path for server configuration file.
            client_cfg (str): File path for client configuration file.
        
        '''
        if((self.mode == "server") or (self.mode == "relay")):
            self.load_server_cfg(server_cfg)
        if((self.mode == "client") or (self.mode == "relay")):
            self.load_client_cfg(client_cfg)
    

    def load_server_cfg(self, cfg_file: str) -> None:
        '''Load configuration data for server from file.

        Parameters:
            cfg_file (str): File path for configuration file.
        
        '''
        cfg_data = None
        with open(cfg_file, 'r') as server_cfg:
            cfg_data = json.load(server_cfg)
        if(self.server_port is None): # Handle port override from argv
            self.server_port = int(cfg_data["connection"]["port"])
        self.keystore.load_server_keys(cfg_data["files"]["public_key"], cfg_data["files"]["private_key"])

    
    def load_client_cfg(self, cfg_file: str) -> None:
        '''Load configuration data for client from file.

        Parameters:
            cfg_file (str): File path for configuration file.

        '''
        cfg_data = None
        with open(cfg_file, 'r') as client_cfg:
            cfg_data = json.load(client_cfg)
        self.keystore.load_client_keys(cfg_data["files"]["public_key"], cfg_data["files"]["private_key"])
        for name in cfg_data["cores"]:
            ip, port = cfg_data["cores"][name].split(':')
            port = int(port)
            self.keystore.add_peer(PeerNode(ip, port, name, True), None)


    def init_components(self) -> None:
        '''Initialize networked components for Node instance.
        
        '''
        try:
            # Initialize server
            if((self.mode == "server") or (self.mode == "relay")):
                self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_sock.bind(('', self.server_port))
            # Initialize client
            if((self.mode == "client") or (self.mode == "relay")):
                self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except OSError as ose:
            print(f"Port {self.server_port} is already bound to a process")
            exit()


    def contact_core(self) -> None:
        '''Contact all members designated as core nodes for their public keys.
        
        '''
        data_packet = Messages.Packet()
        for peer in self.keystore.peer_public_keys.keys():
            print(f"[CLIENT] Requesting key from {peer.ip}")
            # Connect to peer
            self.client_sock.connect((peer.ip, peer.port))
            # Send request for key and await response
            data_packet.construct(Messages.PreambleOnly.MSG_GETKEY, "")
            self.client_sock.send(data_packet.pack())
            data_packet.unpack(self.client_sock.recv(2048))
            if(data_packet._preamble == Messages.PreambleOnly.MSG_BLOCK.value):
                print("[CLIENT] Peer blocked request for key")
                peer_key = None
            elif(data_packet._preamble == Messages.BodyData.MSG_ISKEY.value):
                # Need to get rid of "ISKEY" portion of packet and reencode
                peer_key = data_packet._body
            self.client_sock.close()
            self.keystore.set_peer_key(PeerNode(ip=peer.ip, port=peer.port), peer_key)


    def connect(self, target: PeerNode) -> None:
        '''Open an outgoing connection to a specified peer.

        Parameters:
            target (PeerNode): Target peer node to be connected to.
        
        '''
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_packet = Messages.Packet()
        try:
            self.client_sock.connect((target.ip, target.port))
            data_packet.construct(Messages.PreambleOnly.MSG_HELLO, '')
            self.client_sock.send(data_packet.pack())
        except Exception as e:
            print("[CLIENT] Unable to connect with server")
            print(f"        |-> {e}")


    def list_peers(self) -> None:
        '''Print a list of peers that are currently known to exist.
        
        '''
        for peer in self.keystore.peer_public_keys.keys():
            print(peer)

    
    def show_route(self) -> None:
        '''Print the current route the client has chosen.
        
        '''
        print("[CLIENT] Current route:")
        for peer in self.route:
            print('\t' + str(peer))

    
    def clear_route(self) -> None:
        '''Unroute all peers.
        
        '''
        print("[CLIENT] Unrouted all peers")
        self.route.clear()

    
    def route_peer(self, peer: PeerNode) -> None:
        '''Add a peer to the route using their IP address and target port.

        Parameters:
            ip (str): The IP address of the designated peer.
            port (int): The port at which the peer will be contacted through.
        
        '''
        peer = self.keystore.get_peer(peer) # Get version of the peer stored
        if(peer is not None):
            self.route.append(peer)

    
    def auto_route(self, depth: int) -> None:
        '''Automatically create a route of a given size.

        Parameters:
            depth (int): The number of members involved in the transfer.
        
        '''
        if((type(depth) is int) and (depth > 0)):
            self.route = random.sample(list(self.keystore.peer_public_keys.keys()), k=depth)
        else:
            raise(ValueError("Route size must be a positive integer"))
        

    def hello_packet(self, transfer_size: int = 0) -> Messages.Packet:
        '''Craft a multi-layered, encrypted packet to check if route can send data.
        
        Returns:
            Multi-layer "hello" packet used in transmission.
        '''
        # Create inner-most packet for destination
        stop_packet = Messages.Packet(Messages.MultiPacket.MSG_STOP.value, self.route[-1].ip, self.route[-1].port, transfer_size, b'')
        stop_packet = self.keystore.encrypt_packet(stop_packet, self.route[-1])
        # Wrap destination packet in layers of encryption
        rev_peers = list(reversed(self.route[:-1]))
        layer = stop_packet
        for hop in rev_peers:
            layer = Messages.Packet(Messages.MultiPacket.MSG_FORWARD, hop.ip, hop.port, 0, layer)
            layer = self.keystore.encrypt_packet(layer, hop)
        return Messages.Packet(Messages.MultiPacket.MSG_FORWARD, self.route[0].ip, self.route[0].port, 0, layer)


    
    def layer_packet(self, data: str | bytes) -> Messages.Packet:
        '''
        
        '''
        # Convert string data to bytes
        if(type(data) is str):
            data = data.encode("utf-8")
        # Encryption order is backwards to the routing order
        rev_peers = list(reversed(self.route))
        packet = Messages.Packet(Messages.MultiPacket.MSG_STOP, data)
        packet = self.keystore.encrypt_packet(packet, rev_peers[-1])
        # TODO: Implement the rest of the encryption



    
    def client_as_terminal(self) -> None:
        '''Operate the client as a terminal while connected to the server. This allows the client to
        issue a number of predefined commands directly to the destination.
        
        '''
        do_terminal = True
        data_packet = Messages.Packet()
        while do_terminal:
            # Get output from user and handle each case accordingly
            message = input("> ")
            if(message == "EXIT"):
                data_packet.construct(Messages.PreambleOnly.MSG_EXIT, '')
                self.client_sock.send(data_packet.pack())
                self.client_sock.close()
                do_terminal = False
            elif(message == "SHUTDOWN"):
                data_packet.construct(Messages.DebugMessage.MSG_SHUTDOWN, '')
                self.client_sock.send(data_packet.pack())
                self.client_sock.close()
                do_terminal = False
            elif(message[:5] == "ECHO "):
                data_packet.construct(Messages.BodyData.MSG_ECHO, message[5:])
                self.client_sock.send(data_packet.pack())
                data_packet.unpack(self.client_sock.recv(2048))
                print(f"[CLIENT] Server Echo: {data_packet.body}")
            elif(message == "LIST"):
                self.list_peers()
            elif(message == "ROUTE"):
                self.show_route()
            elif(message == "CLEAR"):
                self.clear_route()
            elif(message[:4] == "HOP "):
                ip, port = message[4:].split(':')
                port = int(port)
                self.route_peer(PeerNode(ip, port))
            elif(message[:10] == "AUTOROUTE "):
                depth = int(message[10:])
                self.auto_route(depth)
            elif(message == "HELLO"):
                packet = self.hello_packet()
                print(len(packet._body))
                print(packet._body)
            elif(message[:5] == "SEND "):
                data = message[5:]
                packet = self.layer_packet(data)
            else:
                data_packet.construct(Messages.BodyData.MSG_DATA, message)
                self.client_sock.send(data_packet.pack())
                data_packet.unpack(self.client_sock.recv(2048))
                print(f"[CLIENT] Server Responded: {data_packet.body}")
    
    
    def start_threads(self) -> None:
        '''Start the thread to run the server separately from the client.
        
        '''
        # TODO: Implement a `run_client()` method
        if(self.mode == "server"):
            self.run_server()
        elif(self.mode == "client"):
            self.contact_core()
            self.connect(PeerNode(ip="127.0.0.1", port=7877))
            self.client_as_terminal()
        else:
            self.server_thread = threading.Thread(target=self.run_server)
            self.server_thread.start()
            sleep(1) # Gives server thread time to start before cores on the same host contact it
            self.contact_core()
            self.connect(PeerNode(ip="127.0.0.1", port=7877))
            self.client_as_terminal()
            self.server_thread.join()


    def run_server(self) -> None:
        '''Run the server component of the Node, which communicates with incoming clients.
        
        '''
        print(f"[SERVER] Running on port {self.server_port}")
        do_server = True
        data_packet = Messages.Packet()
        # Run server process
        while do_server:
            self.server_sock.listen(5)
            conn, addr = self.server_sock.accept()
            data_packet.unpack(conn.recv(2048))
            # NOTE: GETKEY closes connection immediately after sending key
            if(data_packet.preamble == Messages.PreambleOnly.MSG_GETKEY.value):
                print(f"[SERVER] Received key request from {addr}")
                data_packet.construct(Messages.BodyData.MSG_ISKEY, self.keystore.server_keypair.public.public_bytes(encoding=serialization.Encoding.PEM,
                                                                                                                    format=serialization.PublicFormat.SubjectPublicKeyInfo))
                conn.send(data_packet.pack())
                conn.close()
            # NOTE: HELLO starts a new client dialog
            elif(data_packet.preamble == Messages.PreambleOnly.MSG_HELLO.value):
                print(f"[SERVER] Received connection from {addr}")
                do_conn = True
                # Run an active connection with client
                while do_conn:
                    data_packet.unpack(conn.recv(2048))
                    print(f"[SERVER] {addr}: {data_packet}")
                    if(data_packet.preamble == Messages.BodyData.MSG_ECHO.value): # Echo message to client
                        conn.send(data_packet.pack())
                    elif(data_packet.preamble == Messages.PreambleOnly.MSG_EXIT.value): # Client is disconnecting
                        do_conn = False
                    elif(data_packet.preamble == Messages.DebugMessage.MSG_SHUTDOWN.value): # DEBUG: Shutdown server using client
                        do_conn = False
                        do_server = False
                    else: # Message could not be interpreted
                        data_packet.construct(Messages.PreambleOnly.MSG_UNKNOWN, '')
                        conn.send(data_packet.pack())
                conn.close()
            else:
                print(f"[SERVER] Received unknown packet type from client")
                print(f"         |-> {data_packet}")
                data_packet.construct(Messages.PreambleOnly.MSG_UNKNOWN, '')
                conn.send(data_packet.pack())
        print(f"[SERVER] Terminating operation")


# ======================================================================================================================
def create_argv() -> argparse.Namespace:
    '''Parse the command line arguments passed in with the program.

    Returns:
        A namespace through which arguments can be accessed.
    
    '''
    parser = argparse.ArgumentParser(prog="Arbitrary Network",
                                     description="Arbitrary anonymization network",)
    parser.add_argument("--cfg_dir",
                        help="Directory containing configuration files",
                        type=str,
                        default="./cfg")
    parser.add_argument("-p", "--port",
                        help="Port override for server",
                        type=int,)
    parser.add_argument("-m", "--mode",
                        help="Mode override",
                        type=str,
                        choices=["server", "client", "relay", "keygen"],
                        default="relay")
    return parser.parse_args()


# ======================================================================================================================
if __name__ == "__main__":
    argv = create_argv()
    if(argv.mode == "keygen"):
        kgen = KeyStore()
        kgen.gen_keys("keys/server.pub", "keys/server.priv")
        kgen.gen_keys("keys/client.pub", "keys/client.priv")
    else:
        n = Node(argv.cfg_dir, argv.port, argv.mode)
