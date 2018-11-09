from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import PublicFormat
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
if __name__ != "__main__":
    from common import consts

# This file contains various helper functions that wrap the cryptography module
# https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/ for more info


# newPrivateKey -- generates a new RSA private key for signing (and encryption, but we don't do that)
def newPrivateKey():
    return rsa.generate_private_key(
        public_exponent=consts.RSA_EXPONENT,
        key_size=consts.RSA_KEYSIZE, 
        backend=default_backend()
    )

# signMsg -- signs data with privateKey -- returns signature
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

# small amount of code that tests the signing and verification of the cryptography library
if __name__ == "__main__":
    import consts
    private_key = rsa.generate_private_key(
        public_exponent=consts.RSA_EXPONENT, 
        key_size=consts.RSA_KEYSIZE, 
        backend=default_backend()
    )




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
    print(pub.public_numbers())
    print(str(keyToBytes(pub)))
    print(pub.verify(signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    ))

