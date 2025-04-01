from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa



# ======================================================================================================================
class KeyStore(object):
    '''
    
    '''
    def __init__(self, pub_file: str, priv_file: str) -> None:
        '''
        
        '''
        self.public_key:  rsa.RSAPublicKey  = None
        self.private_key: rsa.RSAPrivateKey = None
        self.load_keys(public_key=pub_file, private_key=priv_file)
    


    def gen_keys(self, public_key:str, private_key: str) -> None:
        '''
        
        '''
        # Create keys
        priv = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        pub = priv.public_key()
        # Convert keys to pems
        pem_priv = priv.private_bytes(encoding=serialization.Encoding.PEM,
                                      format=serialization.PrivateFormat.PKCS8,
                                      encryption_algorithm=serialization.NoEncryption())
        pem_pub = pub.public_bytes(encoding=serialization.Encoding.PEM,
                                   format=serialization.PublicFormat.SubjectPublicKeyInfo)
        # Write pem data to files
        with open(private_key, "wb") as key_write:
            key_write.write(pem_priv)
        with open(public_key, "wb") as key_write:
            key_write.write(pem_pub)

        
    def load_keys(self, public_key: str, private_key: str) -> None:
        '''
        
        '''
        try:
            # Load pem keys from files
            with open(public_key, "rb") as key_read:
                self.public_key = serialization.load_pem_public_key(key_read.read(), backend=default_backend())
            with open(private_key, "rb") as key_read:
                self.private_key = serialization.load_pem_private_key(key_read.read(),
                                                                      password=None,
                                                                      backend=default_backend())
        except Exception as e:
            print("[WARN] Could not load key files, generating new ones")
            self.gen_keys(public_key, private_key)
        

    def encrypt(self, data: bytes, key) -> bytes:
        '''
        
        '''
        enc_data = key.encrypt(data, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                  algorithm=hashes.SHA256(),
                                                  label=None))
        return enc_data


    def decrypt(self, data: bytes, key) -> bytes:
        '''
        
        '''
        dec_data = key.decrypt(data,
                               padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                            algorithm=hashes.SHA256(),
                                            label=None))
        return dec_data



# ======================================================================================================================
if __name__ == "__main__":
    print("[ERR] Cannot run KeyStore as standalone instance")
