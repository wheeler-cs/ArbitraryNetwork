import Configuration

import socket

class Server(object):
    '''
    
    '''
    def __init__(self) -> None:
        '''
        
        '''
        self.port: int = Configuration.DEFAULT_PORT
    

    def run(self) -> None:
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.bind(('', self.port))
        self.connection.listen(5)
        print(f"[INFO] Server running on port {self.port}")
        while True:
            conn, addr = self.connection.accept()
            data = conn.recv(1024)
            print(data.decode())
        self.connection.close()


if __name__ == "__main__":
    print("[Running Stand-Alone Server]")
    server = Server()
    server.run()
