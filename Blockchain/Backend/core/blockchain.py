import sys
sys.path.append('F:/00_Github/Crypto_Blockchain')

from Blockchain.Backend.core.block import Block
from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.util.util import hash256, merkle_root, target_to_bits
from Blockchain.Backend.core.database.database import BlockchainDB
import time
from Blockchain.Backend.core.Tx import Coinbase_Tx
from multiprocessing import Process, Manager
from Blockchain.Frontend.run import main


#create the first hash for genesis block
zero_hash = '0' * 64
version = 1
initial_target = 0x0000ffff00000000000000000000000000000000000000000000000000000000

#Create the blockchain
class Blockchain:
    def __init__(self, utxos, MemPool):
        self.utxos = utxos
        self.MemPool = MemPool
        print(f"Blockchain initialized with UTXOS: {utxos} and MemPool: {MemPool}")
        self.current_target = initial_target
        self.bits = target_to_bits(initial_target)

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

    def store_utxos_in_cache(self):
        """Keep track of unspent transactions in cache"""
        for tx in self.add_transactions_in_block:
            print(f"transaction added {tx.TxId}")
            self.utxos[tx.TxId] = tx

    def remove_spent_Transactions(self):
        for tx_id_index in self.remove_spent_transactions:
            if tx_id_index[0].hex() in self.utxos:

                if len(self.utxos[tx_id_index[0].hex()].tx_outs) < 2:
                    print(f"Spent transaction removed {tx_id_index[0].hex()}")
                    del self.utxos[tx_id_index[0].hex()]
                else:
                    prev_transaction = self.utxos[tx_id_index[0].hex()]
                    self.utxos[tx_id_index[0].hex()] = prev_transaction.tx_outs.pop(tx_id_index[1])

    def read_transaction_from_mempool(self):
        """Read transactions from the mempool and store them in a list to be added to the block"""
        self.TxIds = []
        self.add_transactions_in_block = []
        self.remove_spent_transactions = []
        

        for tx in self.MemPool:
            print(f"Reading transaction {tx} from mempool")
            self.TxIds.append(bytes.fromhex(tx))
            self.add_transactions_in_block.append(self.MemPool[tx])

            for spent in self.MemPool[tx].tx_ins:
                self.remove_spent_transactions.append([spent.prev_tx, spent.prev_index])

    def remove_tx_from_mempool(self):
        """Remove Transactions from MemPool"""
        for tx in self.TxIds:
            if tx.hex() in self.MemPool:
                print(f"Removing transaction {tx.hex()} from mempool")
                del self.MemPool[tx.hex()]


    def convert_to_json(self):
        self.TxJson = []

        for tx in self.add_transactions_in_block:
            self.TxJson.append(tx.to_dict())

    def calculate_fee(self):
        """
        Calculates the transaction fee for a block in the blockchain.

        The transaction fee is the difference between the input amount and the output amount. 
        The input amount is the total value of all inputs to the transactions in the block. 
        The output amount is the total value of all outputs from the transactions in the block.

        The function iterates over all transactions in the block, and for each transaction, 
        it adds up the values of the inputs and outputs. The fee is then calculated as the 
        difference between the total input and output amounts.

        Attributes:
        self.input_amount (int): The total value of all inputs to the transactions in the block.
        self.output_amount (int): The total value of all outputs from the transactions in the block.
        self.fee (int): The transaction fee, calculated as the difference between the input and output amounts.

        """
        self.input_amount = 0
        self.output_amount = 0

        # Calculate input amount
        for TxId_index in self.remove_spent_transactions:
            if TxId_index[0].hex() in self.utxos:
                self.input_amount += self.utxos[TxId_index[0].hex()].tx_outs[TxId_index[1]].amount

        # Calculate output amount
        for tx in self.add_transactions_in_block:
            for tx_out in tx.tx_outs:
                self.output_amount += tx_out.amount

        # Calculate fee
        self.fee = self.input_amount - self.output_amount


#create subsequent blocks
    def addBlock(self, block_height, prev_block_hash):
        self.read_transaction_from_mempool()
        self.calculate_fee()
        timestamp = int(time.time())
        coinbase_instance = Coinbase_Tx(block_height)
        coinbase_tx = coinbase_instance.Coinbase_Transaction()
        coinbase_tx.tx_outs[0].amount += self.fee

        self.TxIds.insert(0, bytes.fromhex(coinbase_tx.id()))
        self.add_transactions_in_block.insert(0, coinbase_tx)

        merkleRoot = merkle_root(self.TxIds)[::-1].hex()
        blockheader = BlockHeader(version, prev_block_hash, merkleRoot, timestamp, self.bits)
        blockheader.mine(self.current_target)
        self.remove_spent_Transactions()
        self.remove_tx_from_mempool()
        self.store_utxos_in_cache()
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
    