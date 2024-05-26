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
ZERO_HASH = "0" * 64
VERSION = 1
INITIAL_TARGET = 0x0000FFFF00000000000000000000000000000000000000000000000000000000

#Create blockchain
class Blockchain:
    def __init__(self, utxos, MemPool):
        self.utxos = utxos
        self.MemPool = MemPool
        self.current_target = INITIAL_TARGET
        self.bits = target_to_bits(INITIAL_TARGET)

    def write_on_disk(self, block):
        blockchainDB = BlockchainDB()
        blockchainDB.write(block)

    def fetch_last_block(self):
        blockchainDB = BlockchainDB()
        return blockchainDB.lastBlock()
    
#Create First Block
    def GenesisBlock(self):
        BlockHeight = 0
        prevBlockHash = ZERO_HASH
        self.addBlock(BlockHeight, prevBlockHash)

    """ Keep Track of all the unspent Transaction in cache memory"""

    def store_uxtos_in_cache(self):
        for tx in self.addTransactionsInBlock:
            print(f"Transaction added {tx.TxId} ")
            self.utxos[tx.TxId] = tx

    def remove_spent_Transactions(self):
        for txId_index in self.remove_spent_transactions:
            if txId_index[0].hex() in self.utxos:

                if len(self.utxos[txId_index[0].hex()].tx_outs) < 2:
                    print(f" Spent Transaction removed {txId_index[0].hex()} ")
                    del self.utxos[txId_index[0].hex()]
                else:
                    prev_trans = self.utxos[txId_index[0].hex()]
                    self.utxos[txId_index[0].hex()] = prev_trans.tx_outs.pop(
                        txId_index[1]
                    )

    """ Read Transactions from Memory Pool"""

    def read_transaction_from_memorypool(self):
        self.Blocksize = 80
        self.TxIds = []
        self.addTransactionsInBlock = []
        self.remove_spent_transactions = []

        for tx in self.MemPool:
            self.TxIds.append(bytes.fromhex(tx))
            self.addTransactionsInBlock.append(self.MemPool[tx])
            self.Blocksize += len(self.MemPool[tx].serialize())

            for spent in self.MemPool[tx].tx_ins:
                self.remove_spent_transactions.append([spent.prev_tx, spent.prev_index])

    """ Remove Transactions from Memory pool """

    def remove_transactions_from_memorypool(self):
        for tx in self.TxIds:
            if tx.hex() in self.MemPool:
                del self.MemPool[tx.hex()]

    def convert_to_json(self):
        self.TxJson = []
        for tx in self.addTransactionsInBlock:
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

        for TxId_index in self.remove_spent_transactions:
            if TxId_index[0].hex() in self.utxos:
                self.input_amount += (
                    self.utxos[TxId_index[0].hex()].tx_outs[TxId_index[1]].amount
                )

        """ Calculate Output Amount """
        for tx in self.addTransactionsInBlock:
            for tx_out in tx.tx_outs:
                self.output_amount += tx_out.amount

        self.fee = self.input_amount - self.output_amount

        #create subsequent blocks

    def addBlock(self, BlockHeight, prevBlockHash):
        self.read_transaction_from_memorypool()
        print(f"Block {BlockHeight} read from mempool")

        self.calculate_fee()
        timestamp = int(time.time())
        coinbaseInstance = Coinbase_Tx(BlockHeight)
        coinbaseTx = coinbaseInstance.Coinbase_Transaction()
        self.Blocksize += len(coinbaseTx.serialize())

        coinbaseTx.tx_outs[0].amount = coinbaseTx.tx_outs[0].amount + self.fee

        self.TxIds.insert(0, bytes.fromhex(coinbaseTx.id()))
        self.addTransactionsInBlock.insert(0, coinbaseTx)

        merkleRoot = merkle_root(self.TxIds)[::-1].hex()

        blockheader = BlockHeader(
            VERSION, prevBlockHash, merkleRoot, timestamp, self.bits
        )
        blockheader.mine(self.current_target)
        self.remove_spent_Transactions()
        self.remove_transactions_from_memorypool()
        print(f"Transactions {BlockHeight} removed from mempool")

        self.store_uxtos_in_cache()
        self.convert_to_json()

        print(
            f"Block {BlockHeight} mined successfully with Nonce value of {blockheader.nonce}"
        )
        self.write_on_disk(
            [
                Block(
                    BlockHeight, self.Blocksize, blockheader.__dict__, 1, self.TxJson
                ).__dict__
            ]
        )
#Add new blocks to the chain

    def main(self):
        lastBlock = self.fetch_last_block()
        if lastBlock is None:
            self.GenesisBlock()

        while True:
            lastBlock = self.fetch_last_block()
            BlockHeight = lastBlock["Height"] + 1
            print(f"Current Block Height is is {BlockHeight}")
            prevBlockHash = lastBlock["BlockHeader"]["blockHash"]
            self.addBlock(BlockHeight, prevBlockHash)
            
if __name__ == "__main__":
    with Manager() as manager:
        utxos = manager.dict()
        MemPool = manager.dict()
        print(f"Manager started with UTXOS: {utxos} and MemPool: {MemPool}")  # Print the initial UTXOS and MemPool

        webapp = Process(target=main, args=(utxos, MemPool))
        webapp.start()

        blockchain = Blockchain(utxos, MemPool)
        blockchain.main()
    