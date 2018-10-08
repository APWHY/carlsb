# carlsb

need to fill this in with useful stuff later 



The project is broken into three parts: the blockchain, the carlsb networking code, and the contract wrapper that connects the two together

This readme will demonstrate how to set up a private Ethereum network and connect it to the carlsb network with a contract wrapper. Nodes can (and most should) run the carlsb networking code on its own, with only the cluster heads also needing the contract code as they are the ones connecting to the blockchain.


# Requirements

* Python 3.6
* The `cryptography` library (https://cryptography.io/en/latest/)
    available by running `pip install cryptography` on windows. On other systems follow steps listed here: https://cryptography.io/en/latest/installation/

---
If using Ethereum as an attached blockchain, then these are required:
* `geth` (go-ethereum)
* `web3.py` (via `pip` -- our python interface for interacting with `geth`)
* A 64-bit environment to mine on
* `solc` (solidity compiler)
* `py-solc` (python library to call solc)

# Setup (cluster member)
 Simply clone the project and play around with the examples

# Setup (cluster head)
 Install `geth` (and `golang` if you don't already have it). Again, make sure your device is 64-bit or it will not be able to mine transactions into the network.

 After creating a private network (using your custom `genesis.json` file), look inside your `datadir` for a file called `geth.ipc`. This is the path that you will need to enter into `<insert location here>`.  

 More stuff....

 # Things not yet implemented!
 * CM's and CH's don't forget the other nodes that they are connected to (there is no ttl system anywhere in the code)
 * KUI intervals have not been implemented (although the relevante packer has been written)
 * Consider rewriting packers.py so it becomes a little more flexible
 * Write wrappers for cryptostuff.verifyMsg and cryptostuff.signMsg in CM and CH so we don't need to import cryptostuff in demo-level code