import web3
import json
import os

from web3 import Web3
from solc import compile_source
from web3.contract import ConciseContract


# Solidity source code
contract_source_code = '''
pragma solidity ^0.4.7;
 
contract Factory {
    mapping(bytes => address) chain;
 
    constructor() public {
   
    }
 
    function addMember(bytes pubKey, bytes signature) public {
        if (chain[pubKey] > 0) return;
        address newAddress = new Individual(signature);
        chain[pubKey] = newAddress;
 
    }
 
    function getMember(bytes pubKey) view public returns (address) {
        return chain[pubKey];
    }
}
 
contract Individual {
    mapping(bytes => bool) chain;
 
    constructor(bytes signature) public {
        chain[signature] = true;
    }
 
    function addSignature(bytes signature) public {
        chain[signature] = true;
    }
 
    function checkSignature(bytes signature) view public returns (bool){
        return chain[signature];
    }
}
'''

ipcLocation = "../chain/easy/geth.ipc"
accPassword = "hancott" # I don't know how to make a password-less account 
                        # so this has a password
filename = './factory.contract'

class ContractManager():


    def __init__(self):
        try:
            my_provider = Web3.IPCProvider(ipcLocation)
        except FileNotFoundError as e:
            raise FileNotFoundError("Problem using IPC handle for blockchain at " + ipcLocation + ". Have you forgotten to start one up? Original raised exception was: " + e)
        
        self.compiled_sol = compile_source(contract_source_code) # Compiled source code
    
        self.factory_interface = self.compiled_sol['<stdin>:Factory']
        self.individual_interface = self.compiled_sol['<stdin>:Individual']

        self.w3 = Web3(my_provider)
        self.w3.personal.unlockAccount(self.w3.personal.listAccounts[0],accPassword,150000)
        self.w3.eth.defaultAccount = self.w3.eth.accounts[0]
        print(self.w3.personal.listAccounts[0])
        # Retrieve factory contract if it already exists
        if os.path.isfile(filename):
            f = open(filename)
            oldAddress = f.read()
            print('Factory contract already contracted at address:')
            print(oldAddress)
            self.factory = self.w3.eth.contract(
                address=oldAddress,
                abi=self.factory_interface['abi'],
            )  
        else: # if we must deploy the first instance of the factory contract
            # Instantiate and deploy contract
            FactoryContract = self.w3.eth.contract(abi=self.factory_interface['abi'], bytecode=self.factory_interface['bin'])
        
            # Submit the transaction that deploys the contract
            tx_hash = FactoryContract.constructor().transact()
        
            # Wait for the transaction to be mined, and get the transaction receipt
            tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        
            # Create the contract instance with the newly-deployed address
            print('Factory contract not found -- creating now...')
            self.factory = self.w3.eth.contract(
                address=tx_receipt.contractAddress,
                abi=self.factory_interface['abi'],
            )
            f = open(filename,"x") # save the address of the contract to file
            f.write(tx_receipt.contractAddress)

    # given a contract address and the signature of the message sent, will add it to the chain
    def postMsg(self, addr, sig):    
        target = self.w3.eth.contract(
            address = addr,
            abi=individual_interface['abi'],
        )
        tx_hash = target.functions.addSignature(sig).transact()
        # Wait for transaction to be mined...
        self.w3.eth.waitForTransactionReceipt(tx_hash)

    # given a public key and the signature of message sent, will first create a new contract instance for that node
    # then add the message sent to the blockchain
    def addNode(self, pubkey, sig):
        tx_hash = self.factory.functions.addMember(pubkey,sig).transact()
        # Wait for transaction to be mined...
        self.w3.eth.waitForTransactionReceipt(tx_hash)

    # checks if node with contract at addr has sent a message with signature sig
    def checkMsg(self, addr, sig):
        target = self.w3.eth.contract(
            address = addr,
            abi=self.individual_interface['abi'],
        )

        check = target.functions.checkSignature(sig).call()
        return check

    # given a public key will try to return the address of the contract for that node
    def getNode(self, pubKey):
        return self.factory.functions.getMember(pubKey).call()


if __name__ == "__main__":

    compiled_sol = compile_source(contract_source_code) # Compiled source code
    
    factory_interface = compiled_sol['<stdin>:Factory']
    individual_interface = compiled_sol['<stdin>:Individual']
    # f = open('./gg',"x")
    # import json
    
    # f.write(json.dumps(compiled_sol))
    # os._exit(0) 
    
    
    # web3.py instance
    
    my_provider = Web3.IPCProvider(ipcLocation)

    w3 = Web3(my_provider)
    print(w3.eth.hashrate)
    
    
    w3.personal.unlockAccount(w3.personal.listAccounts[0],accPassword,150000)
    # set pre-funded account as sender
    w3.eth.defaultAccount = w3.eth.accounts[0]
    
    if os.path.isfile(filename):
        f = open(filename)
        oldAddress = f.read()
        print('Factory contract already contracted at address:')
        print(oldAddress)
        factory = w3.eth.contract(
            address=oldAddress,
            abi=factory_interface['abi'],
        )  
    else:
        # Instantiate and deploy contract
        Factory = w3.eth.contract(abi=factory_interface['abi'], bytecode=factory_interface['bin'])
    
        # Submit the transaction that deploys the contract
        tx_hash = Factory.constructor().transact()
    
        # Wait for the transaction to be mined, and get the transaction receipt
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    
        # Create the contract instance with the newly-deployed address
        print('Factory contract not found -- creating now...')
        factory = w3.eth.contract(
            address=tx_receipt.contractAddress,
            abi=factory_interface['abi'],
        )
        f = open(filename,"x")
        f.write(tx_receipt.contractAddress)
    
    
    # Display the default greeting from the contract
    print('Attempting to create indidvidual key:abc sig:123 if not already existing...')
    tx_hash = factory.functions.addMember('abc','123').transact()
    # Wait for transaction to be mined...
    w3.eth.waitForTransactionReceipt(tx_hash)
    abc_address = factory.functions.getMember('abc').call()
    print('Check if abc now has its own contract: {}'.format(abc_address))
    
    abc = w3.eth.contract(
        address = abc_address,
        abi=individual_interface['abi'],
    )
    
    print('Checking signature is stored in contract for abc')
    check = abc.functions.checkSignature('123').call()
    print(check)
    
    print('adding new signature for abc')
    tx_hash = abc.functions.addSignature('x3333').transact()
    # Wait for transaction to be mined...
    w3.eth.waitForTransactionReceipt(tx_hash)
    
    print('checking if new signature x3333 is in abc')
    check = abc.functions.checkSignature('x3333').call()
    print(check)
    
    print('checking if new signature xc3 is in abc')
    check = abc.functions.checkSignature('xc3').call()
    print(check)
    
    print('Attempting to create indidvidual key:def sig:456 if not already existing...')
    tx_hash = factory.functions.addMember('defg','456').transact()
    # Wait for transaction to be mined...
    w3.eth.waitForTransactionReceipt(tx_hash)
    defg_address = factory.functions.getMember('defg').call()
    print('Check if defg now has its own contract: {}'.format(defg_address))
    
    defg = w3.eth.contract(
        address = defg_address,
        abi=individual_interface['abi'],
    )
    
    print('Checking signature is stored in contract for defg')
    check = defg.functions.checkSignature('456').call()
    print(check)
    print('Checking impossible signature is stored in contract for defg')
    check = defg.functions.checkSignature('holy shit').call()
    print(check)
    
    # Display the new greeting value
    # print('Updated contract greeting: {}'.format(
    #     factory.functions.greet().call()
    # ))
    
    # When issuing a lot of reads, try this more concise reader:
    # reader = ConciseContract(factory)
    # assert reader.greet() == "Nihao"