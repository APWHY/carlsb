# carlsb

need to fill this in with useful stuff later 



The project is broken into three parts: the blockchain, the carlsb networking code, and the contract wrapper that connects the two together

This readme will demonstrate how to set up a private Ethereum network and connect it to the carlsb network with a contract wrapper. Nodes can (and most should) run the carlsb networking code on its own, with only the cluster heads also needing the contract code as they are the ones connecting to the blockchain.


# Requirements

* Python 3.6
* The `cryptography` library (https://cryptography.io/en/latest/)
    available by running `pip install cryptography` on windows. On other systems follow steps listed here: https://cryptography.io/en/latest/installation/
    * Raspberry Pi users might additionally need to install `packaging` using `pip` or `pip3`

---
If using Ethereum as an attached blockchain, then these are required (for Cluster Heads):
* `geth` (go-ethereum)
* `web3.py` (via `pip` -- our python interface for interacting with `geth`)
* A 64-bit environment to mine on
* `solc` (solidity compiler)
* `py-solc` (python library to call solc)

# Setup (Cluster Member)
 Simply clone the project and play around with the examples

# Setup (Cluster Head)
 Install `geth` (and `golang` if you don't already have it) along with other dependencies required for an Ethereum implementation. If using your own then you can ignore this.

 After creating a private network using your custom `genesis.json` file (turn down the difficulty!), look inside your `datadir` for a file called `geth.ipc`. This is the path that you will need to enter into `ipcLocation` in `contractCaller.py`.  


 # Things not yet implemented!
 * CM's don't disconnect from CHs for any reason (mainly because there is no reason for them to do so yet)
 * Consider rewriting packers.py so it becomes a little more flexible
