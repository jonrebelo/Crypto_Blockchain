import sys
sys.path.append('F:/00_Github/Crypto_Blockchain')

from Blockchain.Backend.core.block import Block
from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.util.util import hash256
from Blockchain.Backend.core.database.database import BlockchainDB
import time
from Blockchain.Backend.core.Tx import Coinbase_Tx
from multiprocessing import Process, Manager
from Blockchain.Frontend.run import main


#create the first hash for genesis block
zero_hash = '0' * 64
version = 1
#Create the blockchain
class Blockchain:
    def __init__(self, utxos, MemPool):
        self.utxos = utxos
        self.MemPool = MemPool
        print(f"Blockchain initialized with UTXOS: {utxos} and MemPool: {MemPool}") 

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

    def store_utxos_in_cache(self, Transaction):
        """Keep track of unspent transactions in cache"""
        self.utxos[Transaction.TxId] = Transaction

    def read_transaction_from_mempool(self):
        """Read transactions from the mempool and store them in a list to be added to the block"""
        self.TxIds = []
        self.add_transactions_in_block = []
        

        for tx in self.MemPool:
            print(f"Reading transaction {tx} from mempool")
            self.TxIds.append(tx)
            self.add_transactions_in_block.append(self.MemPool[tx])

    def convert_to_json(self):
        self.TxJson = []

        for tx in self.add_transactions_in_block:
            self.TxJson.append(tx.to_dict())

#create subsequent blocks
    def addBlock(self, block_height, prev_block_hash):
        self.read_transaction_from_mempool()
        timestamp = int(time.time())
        coinbase_instance = Coinbase_Tx(block_height)
        coinbase_tx = coinbase_instance.Coinbase_Transaction()

        self.TxIds.insert(0, coinbase_tx.TxId)
        self.add_transactions_in_block.insert(0, coinbase_tx)

        merkleRoot = coinbase_tx.TxId
        bits = 'ffff001f'
        blockheader = BlockHeader(version, prev_block_hash, merkleRoot, timestamp, bits)
        blockheader.mine()
        self.store_utxos_in_cache(coinbase_tx)
        self.convert_to_json()
        print(f"Block {block_height} mined successfully with Nonce value {blockheader.nonce}")
        self.write_on_disk([Block(block_height, 1, blockheader.__dict__, 1, self.TxJson).__dict__])
        print(f"Block {block_height} written on disk")
        self.write_on_disk([Block(block_height, 1, blockheader.__dict__, 1, self.TxJson).__dict__])
        
#Add new blocks to the chain
    def main(self):
        lastBlock = self.fetch_last_block()
        if lastBlock is None:
            print("Creating genesis block")
            self.GenesisBlock()
        while True:
            #Locate last block
            lastBlock = self.fetch_last_block()
            #Add 1 to the last block height
            block_height = lastBlock["Height"] + 1
            #Retrieve the last block hash
            prev_block_hash = lastBlock["BlockHeader"]["blockHash"]
            #pass to addBlock method
            print(f"Adding block {block_height} to the blockchain")
            self.addBlock(block_height, prev_block_hash)



if __name__ == "__main__":
    with Manager() as manager:
        utxos = manager.dict()
        MemPool = manager.dict()

        print(f"Manager started with UTXOS: {utxos} and MemPool: {MemPool}")  # Print the initial UTXOS and MemPool

        #Start the frontend on a separate process
        webapp = Process(target=main, args=(utxos, MemPool))
        webapp.start()
        
        blockchain = Blockchain(utxos, MemPool)
        blockchain.main()
    