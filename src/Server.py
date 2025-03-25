import Configuration

import json
import socket
import threading
from typing import List



# ======================================================================================================================
class Server(object):
    '''Asynchronous, multi-connection socket server.

    Attributes:
        connection (socket.socket): Server-side connection listening for new clients.
        port (int): Port on which server is set to listen.

        max_conns (int): Maximum number of clients able to connect to server.
        conn_list (List[threading.Thread]): List of threads containing connections with clients.
    '''
    def __init__(self, cfg_file: str = "cfg/core.json") -> None:
        '''Server class initializer.

        Initializes all member variables and binds server listening connection to desired port.

        Args:
            cfg_file (str): Path to file containing configuration information for the server.
        
        '''
        # Connection information
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port:         int = Configuration.DEFAULT_PORT
        self.connection.bind(('', self.port))
        # Async management
        self.max_conns:    int                    = Configuration.DEFAULT_MAX_CLIENTS
        self.conn_list:    List[threading.Thread] = list()
        self.collect:      threading.Thread       = threading.Thread(target=self.thread_collect)
        self.collect.start()



    def load_cfg(self, cfg_file: str) -> None:
        '''
        TODO: Implement this
        '''
        cfg_data = None
        with open(cfg_file, 'r') as cfg_read:
            cfg_data = json.load(cfg_read)
        print(cfg_data)


    def async_conn(self, conn: socket.socket, addr) -> None:
        '''Asynchronous connection running in own thread upon successful connection with client.

        Args:
            conn (socket.socket): Connection object streaming data between client and server.
            addr (socket._RetAddress): Return address for client.
        '''
        print(f"[INFO] Established connection with {addr} ({len(self.conn_list)}/{self.max_conns})")
        while True:
            data = conn.recv(2048)
            dec_data = data.decode()
            if(dec_data == "EXIT"):
                conn.send("EXIT".encode())
                print(f"{addr} disconnected")
                break
            else:
                print(f"{addr}: {dec_data}")
            conn.send(data)
        conn.close()
    

    def thread_collect(self):
        '''
        
        '''
        print("[INFO] Watching for dead threads")
        # Reap zombie threads
        for thread in self.conn_list:
            thread.join(0.5)
            if(not(thread.is_alive())):
                print(f"Reaping thread: {thread}")
                self.conn_list.remove(thread)


    def run(self) -> None:
        self.connection.listen(5)
        print(f"[INFO] Server running on port {self.port}")
        while True:
            # Listen for connection attempts
            conn, addr = self.connection.accept()
            if(len(self.conn_list) < self.max_conns):
                self.conn_list.append(threading.Thread(target=self.async_conn, args=(conn, addr)))
                self.conn_list[-1].start()
            else: # Connections maxxed; clear buffer and send BLOCK
                data = conn.recv(2048)
                conn.send("BLOCK".encode())
                conn.close()



# ======================================================================================================================
if __name__ == "__main__":
    print("[Running Stand-Alone Server]")
    server = Server()
    server.run()
