from Configuration import Configuration

import socket

class Server(object):
    '''
    
    '''

    def __init__(self, cfg: Configuration) -> None:
        '''
        
        '''
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.bind(('', cfg.listen_port))
        self.connection.listen(cfg.server_max_clients)
