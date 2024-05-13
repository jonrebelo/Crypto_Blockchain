import sys
sys.path.append('F:/00_Github/Crypto_Blockchain')

from Blockchain.Backend.core.block import Block
from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.util.util import hash256
import time
import json

#create the first hash for genesis block
zero_hash = '0' * 64
version = 1
#Create the blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.GenesisBlock()

#create the first block
    def GenesisBlock(self):
        BlockHeight = 0
        prevBlockHash = zero_hash
        self.addBlock(BlockHeight, prevBlockHash)

    def addBlock(self, BlockHeight, prevBlockHash):
        timestamp = int(time.time())
        Transaction = f"""I used to think that the day would never come.. I'd see delight in the shade of the morning sun.. My morning sun is the drug that brings me near.. To the childhood I lost, replaced by fear..  I used to think that the day would never come.. That my life would depend on the morning sun {BlockHeight}"""
        merkleRoot = hash256(Transaction.encode()).hex()
        bits = 'ffff001f'
        blockheader = BlockHeader(version, prevBlockHash, merkleRoot, timestamp, bits)
        blockheader.mine()
        self.chain.append(Block(BlockHeight, 1, blockheader.__dict__, 1, Transaction).__dict__)
        print(json.dumps(self.chain, indent = 4))
        
#Add new blocks to the chain
    def main(self):
        while True:
            lastBlock = self.chain[::-1]
            BlockHeight = lastBlock[0]["Height"] + 1

if __name__ == "__main__":
    blockchain = Blockchain()