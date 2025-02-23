import json

DEFAULT_NETWORK = "cfg/network.json"



def generate_network(out_file: str = DEFAULT_NETWORK) -> None:
    '''
    
    '''
    cfg_json = {"core_nodes":
                {
                    "ip0": "127.0.0.1",
                    "ip1": "127.0.0.2",
                    "ip2": "127.0.0.3"
                },
                "listen_port": 7877,
                "server_max_clients": 5,
                "client_min_reroute_time": 60,
                "client_max_reroute_time": 300,
               }
    with open("cfg/network.json", 'w') as network_cfg:
        network_cfg.write(json.dumps(cfg_json, indent=4))



if __name__ == "__main__":
    print("[JSON Generation]")
    do_run = True
    while do_run:
        print("\n0) Exit\n1) Network")
        try:
            choice = int(input("> "))
            if(type(choice) is int):
                if(choice == 0):
                    do_run = False
                elif(choice == 1):
                    generate_network()
        except:
            pass