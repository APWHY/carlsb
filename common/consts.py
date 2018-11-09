# simple config(ish) file used to store a bunch of constants. I don't think there will be many
# hence me not bothering with json or yaml

# This is chosen to be the port on which all nodes listen for broadcasts
# In the future this won't be needed when a different method for 
# adding nodes to the network is implemented
BROADCAST_PORT = 28196

# How often we want to broadcast MSG_INTRO (in seconds)
BROADCAST_FREQ = 2

# How often we want CM's to change their public and private keys (in seconds)
# Not currently used TODO
KUI_INTERVAL = 5

# Constants related to key generation
RSA_EXPONENT = 65537
RSA_KEYSIZE = 2048
RSA_KEYBYTESIZE = 426

# Identifiers between CM and CH messages
TYPE_CM = 0
TYPE_CH = 1

# Identifiers between different message types
MSG_INTRO = 0
MSG_TRANS = 1
MSG_ACK = 2
MSG_VERIFY = 3
MSG_KUI = 4 
# The MSG_MSG type is not needed for the network to run but makes notification easier for the demo files
MSG_MSG = 99 

# Next section is message formats. For more info look in packers.py

# PEM serialised public keys are just 451 chars long and IP addresses are 15 chars long
# signatures are 256 chars long

# format is int,int,15 char array,int,451 char array
MSG_INTRO_FMT = 'ii15si451s'
# format is int,int,256 char array,451 char array
MSG_TRANS_FMT = 'ii256s451s'
# format is int,int,15 char array,int,int,451 char array
MSG_ACK_FMT = 'ii15sii451s'
# format is int,int,256 char array,451 char array,451 char array,bool 
MSG_VERIFY_FMT = 'ii256s451s451s?'
# format is int,int,451 char array,451 char array
MSG_KUI_FMT = 'ii451s451s'

# format is int,int,15 char array,int,256 char array,451 char array
MSG_MSG_FMT = 'ii15si256s451s' # this is only to help for demonstration purposes




# port that a recipient expects to find a file on (for demo purposes)
HTTP_PORT = 8088

# size we set our handlers to recv on (atm needs to be more than 1167 for VerifyMsg)
RECV_SIZE = 4096

if __name__ == "__main__":
    print("hello world")