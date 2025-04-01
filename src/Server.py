import Configuration
from KeyStore import KeyStore
from Messages import *

from cryptography.hazmat.primitives import serialization
import json
import socket
import threading
from time import sleep
from typing import Dict, List



# ======================================================================================================================
class Server(object):
    '''Asynchronous, multi-connection socket server.

    Attributes:
        connection (socket.socket): Server-side connection listening for new clients.
        port (int): Port on which server is set to listen.

        max_conns (int): Maximum number of clients able to connect to server.
        conn_list (List[threading.Thread]): List of threads containing connections with clients.
    
    Args:
        cfg_file (str): Path to configuration file to load upon server initializaiton.

    '''
    def __init__(self, cfg_file: str = "cfg/network.json") -> None:
        '''Server class initializer.

        Initializes all member variables and binds server listening connection to desired port.

        Args:
            cfg_file (str): Path to file containing configuration information for the server.
        
        '''
        # Connection information
        self.port: int = Configuration.DEFAULT_PORT
        # Async management
        self.max_conns:        int                    = Configuration.DEFAULT_MAX_CLIENTS
        self.collect_interval: int                    = 30
        self.conn_list:        List[threading.Thread] = list()
        self.collect:          threading.Thread       = threading.Thread(target=self.thread_collect)
        # Security
        self.keystore: KeyStore = None
        # Start server components
        self.load_cfg(cfg_file)
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.bind(('', self.port))
        self.collect.start()


    def load_cfg(self, cfg_file: str) -> None:
        ''' Loads server-related configuration data from provided file.

        Args:
            cfg_file (str): Path to configuration file for server.
        '''
        cfg_data = None
        with open(cfg_file, 'r') as cfg_read:
            cfg_data = json.load(cfg_read)
        self.max_conns = cfg_data["server"]["max_clients"]
        self.collect_interval = cfg_data["server"]["reap_interval"]
        self.port = cfg_data["server"]["listen_port"]
        self.keystore = KeyStore(cfg_data["server"]["public_key"], cfg_data["server"]["private_key"])
    

    def async_conn(self, conn: socket.socket, addr) -> None:
        '''Asynchronous connection running in own thread upon successful connection with client.

        Args:
            conn (socket.socket): Connection object streaming data between client and server.
            addr (socket._RetAddress): Return address for client.
        '''
        print(f"[INFO] Established connection with {addr} ({len(self.conn_list) + 1}/{self.max_conns})")
        while True:
            data = conn.recv(2048)
            if(data == MSG_EXIT): # Cleanly exit
                conn.send(MSG_EXIT)
                print(f"{addr} disconnected")
                break
            elif(data == MSG_NULLSTR): # Happens when client does CTRL + C
                print(f"{addr} is unresponsive")
                break
            elif(data == MSG_GETKEY):
                key_bytes = self.keystore.public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                                  format=serialization.PublicFormat.SubjectPublicKeyInfo)
                message = MSG_ISKEY + key_bytes
                conn.send(message)
            else:
                print(f"{addr}: {data}")
            conn.send(data)
        conn.close()

    
    def thread_collect(self):
        '''Waits for connections to close and reaps thread once terminated.
        
        '''
        while True:
            # Reap zombie threads
            for thread in self.conn_list:
                # If thread hasn't been started when trying to join, an exception is thrown
                try:
                    thread.join(0.001)
                    if(not(thread.is_alive())):
                        self.conn_list.remove(thread)
                except Exception as e:
                    print(f"[WARN] Unable to join thread {thread} currently")
            sleep(self.collect_interval) # Keeps from pinning CPU at 100%


    def run(self) -> None:
        '''Runs asynchronous server, which will accept incoming connections and connect if not maxxed out.
        
        '''
        print(self)
        self.connection.listen(self.max_conns)
        # Asynchronous thread collection
        while True:
            # Listen for connection attempts
            conn, addr = self.connection.accept()
            if(len(self.conn_list) < self.max_conns):
                conn.send(MSG_HELLO)
                # Create new connection thread
                # NOTE: You have to create and start the thread before adding it to the thread list because thread
                # collection is running asynchronously and errors out if the thread isn't started
                conn_thread = threading.Thread(target=self.async_conn, args=(conn, addr))
                conn_thread.start()
                self.conn_list.append(conn_thread)
            else: # Connections maxxed, send BLOCK
                conn.send(MSG_BLOCK)
                conn.close()
    

    def __str__(self) -> str:
        '''Overrides the default __str__ operation to display server information.
        
        '''
        return(f"Forwarding Server\nPort: {self.port}  ||  Max Connections: {self.max_conns}  ||  Collection Interval: {self.collect_interval}\n")



# ======================================================================================================================
if __name__ == "__main__":
    print("[Running Stand-Alone Server]")
    server = Server()
    server.run()
