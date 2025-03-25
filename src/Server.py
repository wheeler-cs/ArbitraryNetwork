import Configuration

import json
import socket
import threading
from typing import List



# ======================================================================================================================
class Server(object):
    '''
    
    '''
    def __init__(self, cfg_file: str = "cfg/core.json") -> None:
        '''
        
        '''
        # Connection information
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port:         int = Configuration.DEFAULT_PORT
        # Async management
        self.active_conns: int                    = 0
        self.max_conns:    int                    = Configuration.DEFAULT_MAX_CLIENTS
        self.conn_list:    List[threading.Thread] = list()
        self.initialize()



    def load_cfg(self, cfg_file: str) -> None:
        # TODO: Implement this
        cfg_data = None
        with open(cfg_file, 'r') as cfg_read:
            cfg_data = json.load(cfg_read)
        print(cfg_data)


    def initialize(self) -> None:
        self.connection.bind(('', self.port))
        print(f"[INFO] Server initialized")

    
    def async_conn(self, conn, addr) -> None:
        print(f"[INFO] Established connection with {addr} ({self.active_conns}/{self.max_conns})")
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
        self.active_conns -= 1


    def run(self) -> None:
        self.connection.listen(5)
        print(f"[INFO] Server running on port {self.port}")
        while True:
            # Listen for connection attempts
            conn, addr = self.connection.accept()
            if(self.active_conns < self.max_conns):
                self.conn_list.append(threading.Thread(target=self.async_conn, args=(conn, addr)))
                self.active_conns += 1
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
