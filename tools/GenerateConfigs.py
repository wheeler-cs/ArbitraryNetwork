import json

DEFAULT_SERVER = "cfg/server.json"
DEFAULT_CLIENT = "cfg/client.json"



def generate_server(out_file: str = DEFAULT_SERVER) -> None:
    '''
    
    '''
    cfg_json = {"connection":
                {
                    "port": "7877"
                },
                "files":
                {
                    "private_key": "keys/server.priv",
                    "public_key": "keys/server.pub",
                }
               }
    with open(out_file, 'w') as server_cfg:
        server_cfg.write(json.dumps(cfg_json, indent=4))


def generate_client(out_file: str = DEFAULT_CLIENT) -> None:
    '''
    
    '''
    cfg_json = {"cores":
                {
                    "basic": "127.0.0.1:7877"
                },
                "connection":
                {
                    "reroute_min": 30,
                    "reroute_max": 180,
                },
                "files":
                {
                    "private_key": "keys/client.priv",
                    "public_key": "keys/client.pub",
                }
               }
    with open(out_file, 'w') as client_cfg:
        client_cfg.write(json.dumps(cfg_json, indent=4))


# ======================================================================================================================
if __name__ == "__main__":
    print("[JSON Generation]")
    do_run = True
    while do_run:
        print("\n0) Exit\n1) Server\n2) Client")
        try:
            choice = int(input("> "))
            if(type(choice) is int):
                if(choice == 0):
                    do_run = False
                elif(choice == 1):
                    generate_server()
                    print("[Server Config Generated]")
                elif(choice == 2):
                    generate_client()
                    print("[Client Config Generated]")
            else:
                print("Please specify a number")
        except Exception as e:
            print(e)