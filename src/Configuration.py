import json
import os

from typing import Set

class Configuration(object):
    '''
    
    '''
    def __init__(self, json_dir: str) -> None:
        '''
        
        '''
        self.core_nodes: Set[str] = set()
        self.listen_port: int = 0
        self.server_max_clients: int = 0

        self.load_json(json_dir)

    
    def load_json(self, json_dir: str) -> None:
        '''
        
        '''
        # Get network configuration info
        with open(os.path.join(json_dir, "network.json"), 'r') as network_cfg:
            network_data = json.load(network_cfg)
        # WARN: This loads the IPs in a nondeterministic order
        self.core_nodes = set(network_data["core_nodes"].values())
        self.listen_port = network_data["listen_port"]
        self.server_max_clients = network_data["server_max_clients"]



if __name__ == "__main__":
    print("[WARN]: Running Configuration as a single file!")
    program_cfg = Configuration("cfg")
