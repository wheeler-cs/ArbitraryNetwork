import Configuration

import socket



# ======================================================================================================================
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
        conn, addr = self.connection.accept()
        while True:
            data = conn.recv(1024)
            decoded_data = data.decode()
            print(decoded_data)
            if(decoded_data == "exit"):
                conn.close()
                break
            else:
                conn.send("Hello".encode())
        self.connection.close()



# ======================================================================================================================
if __name__ == "__main__":
    print("[Running Stand-Alone Server]")
    server = Server()
    server.run()
