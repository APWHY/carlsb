# simple config(ish) file used to store a bunch of constants. I don't think there will be many
# hence me not bothering with json or yaml


BROADCAST_PORT = 28196
    # This is chosen to be the port on which all nodes listen for broadcasts
    # In the future this won't be needed when a different method for 
    # adding nodes to the network is implemented

RSA_EXPONENT = 65537
RSA_KEYSIZE = 2048
RSA_KEYBYTESIZE = 426 #is this always true?????

TYPE_CM = 0
TYPE_CH = 1

MSG_INTRO = 0
MSG_TRANS = 1
MSG_ACK = 2


# PEM serialised public keys are just 451 chars long and IP addresses are 15 chars long
# signatures are 256 chars long

# format is int,int,15 char array,int,451 char array
MSG_INTRO_FMT = 'ii15si451s'
# format is int,int,256 char array,451 char array
MSG_TRANS_FMT = 'ii256s451s'
# format is int,int,15 char array,int,int
MSG_ACK_FMT = 'ii15sii'