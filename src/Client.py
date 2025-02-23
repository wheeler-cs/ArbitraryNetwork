from Configuration import Configuration

import socket

class Client(object):
    '''
    
    '''

    def __init__(self, cfg: Configuration) -> None:
        '''
        
        '''
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
