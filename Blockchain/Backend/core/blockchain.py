import sys
sys.path.append('F:/00_Github/Crypto_Blockchain')

from Blockchain.Backend.core.block import Block
from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.util.util import hash256
from Blockchain.Backend.core.database.database import BlockchainDB
import time
from Blockchain.Backend.core.Tx import Coinbase_Tx


#create the first hash for genesis block
zero_hash = '0' * 64
version = 1
#Create the blockchain
class Blockchain:
    def __init__(self):
        pass

    def write_on_disk (self, block):
        blockchaindb = BlockchainDB()
        blockchaindb.write(block)
    
    def fetch_last_block(self):
        blockchaindb = BlockchainDB()
        return blockchaindb.lastBlock()


#create the first block
    def GenesisBlock(self):
        block_height = 0
        prev_block_hash = zero_hash
        self.addBlock(block_height, prev_block_hash)

#create subsequent blocks
    def addBlock(self, block_height, prev_block_hash):
        timestamp = int(time.time())
        coinbase_instance = Coinbase_Tx(block_height)
        coinbase_tx = coinbase_instance.Coinbase_Transaction()

        merkleRoot = coinbase_tx.TxId
        bits = 'ffff001f'
        blockheader = BlockHeader(version, prev_block_hash, merkleRoot, timestamp, bits)
        blockheader.mine()
        print(f"Block {block_height} mined successfully with Nonce value {blockheader.nonce}")
        self.write_on_disk([Block(block_height, 1, blockheader.__dict__, 1, coinbase_tx.to_dict()).__dict__])
        
#Add new blocks to the chain
    def main(self):
        lastBlock = self.fetch_last_block()
        if lastBlock is None:
            self.GenesisBlock()
        while True:
            #Locate last block
            lastBlock = self.fetch_last_block()
            #Add 1 to the last block height
            block_height = lastBlock["Height"] + 1
            #Retrieve the last block hash
            prev_block_hash = lastBlock["BlockHeader"]["blockHash"]
            #pass to addBlock method
            self.addBlock(block_height, prev_block_hash)



if __name__ == "__main__":
    blockchain = Blockchain()
    blockchain.main()