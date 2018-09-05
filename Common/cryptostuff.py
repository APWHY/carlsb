from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import PublicFormat
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

# This file contains various helper functions that wrap the cryptography module
# https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/ for more info
# TODO clean up the __main__ code

# newPrivateKey -- generates a new RSA private key for signing (and encryption, but we don't do that)
def newPrivateKey():
    return rsa.generate_private_key(
        public_exponent=65537, #use const here
        key_size=2048, #use const here
        backend=default_backend()
    )

# signMsg -- signs data with privateKey
def signMsg(privateKey,data):
    return privateKey.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )


# verifyMsg -- verifies that publicKey's source is legitmate by checking it against signature and message
# Returns True if everything checks out
# Returns False if the signature is invalid
# Will throw an exception if something else goes wrong (like TypeError etc.)
def verifyMsg(publicKey,message,signature):
    try:      
        publicKey.verify(signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except InvalidSignature:
        return False
    return True

# keyToBytes -- wrapper function to serialise a key to bytes    
# this throws an excpetion if the key is private. We should never be serialising private keys!!!
def keyToBytes(publicKey):
    if isinstance(publicKey,rsa.RSAPublicKey):
        return publicKey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    return TypeError

# bytesToKey -- wrapper function to deserialise a serialised key
def bytesToKey(data):
    return serialization.load_pem_public_key(data,backend=default_backend())




if __name__ == "__main__":
    private_key = rsa.generate_private_key(
        public_exponent=65537, #use const here
        key_size=2048, #use const here
        backend=default_backend()
    )
    private_key.private_numbers



    message = b"A message I want to sign"
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    pub = private_key.public_key()
    pub.verify(signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    PublicFormat.p


