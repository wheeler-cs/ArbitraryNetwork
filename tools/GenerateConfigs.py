import json

DEFAULT_NETWORK = "cfg/network.json"



def generate_network(out_file: str = DEFAULT_NETWORK) -> None:
    '''
    
    '''
    cfg_json = {"trusted_cores":
                {
                    "localhost": "127.0.0.1",
                },
                "logging":
                {
                    "log_file": "program.log",
                },
                "client":
                {
                    "packet_size": 1024,
                    "min_reroute_timeout": 60,
                    "max_reroute_timeout": 300,
                },
                "server":
                {
                    "listen_port": 7877,
                    "max_clients": 5,
                }
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