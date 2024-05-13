import sys
sys.path.append('F:/00_Github/Crypto_Blockchain')

from Blockchain.Backend.core.block import Block
from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.util.util import hash256
from Blockchain.Backend.core.database.database import BlockchainDB
import time

#create the first hash for genesis block
zero_hash = '0' * 64
version = 1
#Create the blockchain
class Blockchain:
    def __init__(self):
        self.GenesisBlock()

    def write_on_disk (self, block):
        blockchaindb = BlockchainDB()
        blockchaindb.write(block)
    
    def fetch_last_block(self):
        blockchaindb = BlockchainDB()
        return blockchaindb.lastBlock()


#create the first block
    def GenesisBlock(self):
        BlockHeight = 0
        prevBlockHash = zero_hash
        self.addBlock(BlockHeight, prevBlockHash)

#create subsequent blocks
    def addBlock(self, BlockHeight, prevBlockHash):
        timestamp = int(time.time())
        Transaction = f"""{BlockHeight} units have been sent"""
        merkleRoot = hash256(Transaction.encode()).hex()
        bits = 'ffff001f'
        blockheader = BlockHeader(version, prevBlockHash, merkleRoot, timestamp, bits)
        blockheader.mine()
        self.write_on_disk([Block(BlockHeight, 1, blockheader.__dict__, 1, Transaction).__dict__])
        
#Add new blocks to the chain
    def main(self):
        while True:
            #Locate last block
            lastBlock = self.fetch_last_block()
            #Add 1 to the last block height
            BlockHeight = lastBlock["Height"] + 1
            #Retrieve the last block hash
            prevBlockHash = lastBlock["BlockHeader"]["blockHash"]
            #pass to addBlock method
            self.addBlock(BlockHeight, prevBlockHash)

if __name__ == "__main__":
    blockchain = Blockchain()
    blockchain.main()