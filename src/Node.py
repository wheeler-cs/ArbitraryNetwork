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
        '''Class initializer for `Node` class.

        Parameters:
            cfg_dir (str): Directory containing the configuration files for the server and client.
            port (Union[int, None]): The port to listen for connections.
            mode (str): The mode the server should run in.
        
        '''
        # Functionality information
        self.mode:          str              = mode
        self.route:         List[PeerNode]   = list()
        # Server variables
        self.server_port:   int              = port
        self.server_sock:   socket.socket    = None
        self.server_conn:   socket.socket    = None
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
            data_packet.construct(Messages.PreambleOnly.MSG_GETKEY, peer.ip, peer.port, 0, "")
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
            data_packet.construct(Messages.PreambleOnly.MSG_HELLO, '', 0, 0, '')
            self.client_sock.send(data_packet.pack())
        except Exception as e:
            print("[CLIENT] Unable to connect with server")
            print(f"        |-> {e}")

    
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
        print(f"[CLENT] Added {peer} to end of current route")
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
        
    
    def open_route(self) -> None:
        '''
        
        '''
        print("[CLIENT] Preparing route for transfer...")
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hello_packet = self.hello_packet(0)
        self.client_sock.connect((self.route[0].ip, self.route[0].port))
        self.client_sock.send(hello_packet.pack())
        reply = self.client_sock.recv(2048)
        print("[CLIENT] Route established")
        

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
            layer = Messages.Packet(Messages.MultiPacket.MSG_FORWARD.value, hop.ip, hop.port, 0, layer)
            layer = self.keystore.encrypt_packet(layer, hop)
        return Messages.Packet(Messages.MultiPacket.MSG_FORWARD.value, self.route[0].ip, self.route[0].port, 0, layer)

    
    def start_threads(self) -> None:
        '''Start the thread to run the server separately from the client.
        
        '''
        if(self.mode == "server"):
            self.run_server()
        elif(self.mode == "client"):
            self.run_client()
        else:
            self.server_thread = threading.Thread(target=self.run_server)
            self.server_thread.start()
            sleep(1) # Gives server thread time to start before cores on the same host contact it
            self.client_thread = threading.Thread(target=self.run_client)
            self.client_thread.start()
            self.client_thread.join()
            self.server_thread.join()

    
    def run_client(self) -> None:
        '''
        
        '''
        # TODO: Make this more flushed out
        self.client_demo()

    
    def client_demo(self) -> None:
        '''
        
        '''
        # Get list of nodes and make a route
        self.contact_core()
        self.auto_route(1)
        # Establish route with nodes
        self.route_peer(PeerNode("127.0.0.1", 7877))
        self.open_route()
        # Send message to destination

        # Receive reply

        # End connection


    def run_server(self) -> None:
        '''Run the server component of the Node, which communicates with incoming clients.
        
        '''
        print(f"[SERVER] Running on port {self.server_port}")
        do_server = True
        data_packet = Messages.Packet()
        # Run server process
        while do_server:
            self.server_sock.listen(5)
            self.server_conn, _ = self.server_sock.accept()
            data_packet.unpack(self.server_conn.recv(2048))
            # NOTE: GETKEY closes connection immediately after sending key
            if(data_packet.preamble == Messages.PreambleOnly.MSG_GETKEY.value):
                data_packet.construct(Messages.BodyData.MSG_ISKEY, "", 0, 0, self.keystore.server_keypair.public.public_bytes(encoding=serialization.Encoding.PEM,
                                                                                                                              format=serialization.PublicFormat.SubjectPublicKeyInfo))
                self.server_conn.send(data_packet.pack())
                self.server_conn.close()
            elif(data_packet.preamble == Messages.PreambleOnly.MSG_HELLO.value):
                self.server_loop()
        print(f"[SERVER] Terminating operation")


    def server_loop(self) -> None:
            '''

            '''
            data_packet = Messages.Packet()
            do_conn = True
            while do_conn:
                data_packet.unpack(self.server_conn.recv(2048))
                print(f"[SERVER] Data Recieved: {data_packet}")
                # Forward packet to next hop, and wait for a reply
                if(data_packet.preamble == Messages.MultiPacket.MSG_FORWARD.value):
                    forward_node = PeerNode(data_packet._dest_ip, data_packet._dest_port)
                    self.connect(forward_node)



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
