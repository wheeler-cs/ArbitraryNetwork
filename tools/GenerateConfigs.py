import json

DEFAULT_NETWORK = "cfg/network.json"
DEFAULT_CORE    = "cfg/core.json"
DEFAULT_CLIENT  = "cfg/client.json"



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
                    "min_reroute_timeout": 60,
                    "max_reroute_timeout": 300,
                },
                "server":
                {
                    "listen_port": 7877,
                    "max_clients": 5,
                    "reap_interval": 20,
                }
               }
    with open("cfg/network.json", 'w') as network_cfg:
        network_cfg.write(json.dumps(cfg_json, indent=4))


def generate_core(out_file: str = DEFAULT_CORE) -> None:
    '''
    
    '''
    cfg_json = {"core_members":
                {
                    "alpha": "127.0.0.1:9801",
                    "beta": "127.0.0.1:9802",
                },
                "files":
                {
                    "private_key": "keys/key.priv",
                    "public_key": "keys/key.pub",
                }
               }
    with open(out_file, 'w') as core_cfg:
        core_cfg.write(json.dumps(cfg_json, indent=4))


def generate_client(out_file: str = DEFAULT_CLIENT) -> None:
    '''
    
    '''
    cfg_json = {"cores":
                {
                    "basic": "127.0.0.1:62500"
                },
                "files":
                {
                    "private_key": "keys/client.priv",
                    "public_key": "keys/client.pub",
                }
               }
    with open(out_file, 'w') as client_cfg:
        client_cfg.write(json.dumps(cfg_json, indent=4))


if __name__ == "__main__":
    print("[JSON Generation]")
    do_run = True
    while do_run:
        print("\n0) Exit\n1) Network\n2) Core\n3) Client")
        try:
            choice = int(input("> "))
            if(type(choice) is int):
                if(choice == 0):
                    do_run = False
                elif(choice == 1):
                    generate_network()
                    print("[Network Config Generated]")
                elif(choice == 2):
                    generate_core()
                    print("[Core Config Generated]")
                elif(choice == 3):
                    generate_client()
                    print("[Client Config Generated]")
            else:
                print("Please specify a number")
        except Exception as e:
            print(e)