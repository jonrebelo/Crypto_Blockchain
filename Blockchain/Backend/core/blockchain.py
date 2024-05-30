import sys
sys.path.append('F:/00_Github/Crypto_Blockchain')
import configparser
import copy
from Blockchain.Backend.core.block import Block
from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.util.util import hash256, merkle_root, target_to_bits, bits_to_target
from Blockchain.Backend.core.database.database import BlockchainDB, NodeDB
import time
from Blockchain.Backend.core.Tx import CoinbaseTx, Tx
from multiprocessing import Process, Manager
from Blockchain.Frontend.run import main
from Blockchain.Backend.core.network.sync_manager import syncManager
from Blockchain.client.autoBroadcastTX import autoBroadcast



#create the first hash for genesis block
ZERO_HASH = "0" * 64
VERSION = 1
INITIAL_TARGET = 0x0000FFFF00000000000000000000000000000000000000000000000000000000
MAX_TARGET     = 0x0000ffff00000000000000000000000000000000000000000000000000000000

"""
# Calculate new Target to keep our Block mine time under 20 seconds
# Reset Block Difficulty after every 10 Blocks
"""
AVERAGE_BLOCK_MINE_TIME = 20
RESET_DIFFICULTY_AFTER_BLOCKS = 10
AVERAGE_MINE_TIME = AVERAGE_BLOCK_MINE_TIME * RESET_DIFFICULTY_AFTER_BLOCKS

class Blockchain:
    """Represents a blockchain, with methods for managing blocks, transactions, and the memory pool."""
    def __init__(self, utxos, MemPool, newBlockAvailable, secondaryChain):
        self.utxos = utxos
        self.MemPool = MemPool
        self.newBlockAvailable = newBlockAvailable
        self.secondaryChain = secondaryChain
        self.current_target = INITIAL_TARGET
        self.bits = target_to_bits(INITIAL_TARGET)

    def write_on_disk(self, block):
        """Writes a block to the disk."""
        blockchainDB = BlockchainDB()
        blockchainDB.write(block)

    def fetch_last_block(self):
        """Fetches the last block from the blockchain."""
        blockchainDB = BlockchainDB()
        return blockchainDB.lastBlock()

    def GenesisBlock(self):
        """Creates the genesis block (the first block) in the blockchain."""
        BlockHeight = 0
        prevBlockHash = ZERO_HASH
        self.addBlock(BlockHeight, prevBlockHash)

    def startSync(self, block = None):
        """Starts the synchronization process with other nodes in the network."""
        try:
            node = NodeDB()
            portList = node.read()

            for port in portList:
                if localHostPort != port:
                    sync = syncManager(localHost, port, secondaryChain = self.secondaryChain)
                    try:
                        if block:
                            sync.publishBlock(localHostPort - 1, port, block) 
                        else:                    
                            sync.startDownload(localHostPort - 1, port, True)
                  
                    except Exception as err:
                        pass
                    
        except Exception as err:
            pass
       
    """Stores all unspent transactions in cache"""
    def store_uxtos_in_cache(self):
        for tx in self.addTransactionsInBlock:
            print(f"Transaction added {tx.TxId} ")
            self.utxos[tx.TxId] = tx

    def remove_spent_Transactions(self):
        """Removes spent transactions from the list of unspent transactions."""
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
                    
    def doubleSpendingAttempt(self, tx):
        """Checks if a transaction is a double spending attempt."""
        for txin in tx.tx_ins:
            if txin.prev_tx not in self.prevTxs and txin.prev_tx.hex() in self.utxos:
                self.prevTxs.append(txin.prev_tx)
            else:
                return True

    def read_transaction_from_memorypool(self):
        """Reads transactions from the memory pool and checks for double spending"""
        self.Blocksize = 80
        self.TxIds = []
        self.addTransactionsInBlock = []
        self.remove_spent_transactions = []
        self.prevTxs = []
        deleteTxs = []

        tempMemPool = dict(self.MemPool)
        
        if self.Blocksize < 1000000:
            for tx in tempMemPool:
                if not self.doubleSpendingAttempt(tempMemPool[tx]):
                    tempMemPool[tx].TxId = tx
                    self.TxIds.append(bytes.fromhex(tx))
                    self.addTransactionsInBlock.append(tempMemPool[tx])
                    self.Blocksize += len(tempMemPool[tx].serialize())

                    for spent in tempMemPool[tx].tx_ins:
                        self.remove_spent_transactions.append([spent.prev_tx, spent.prev_index])
                else:
                    deleteTxs.append(tx)
        
        for txId in deleteTxs:
            del self.MemPool[txId]

           
    def remove_transactions_from_memorypool(self):
        """Removes processed transactions from the memory pool."""
        for tx in self.TxIds:
            if tx.hex() in self.MemPool:
                del self.MemPool[tx.hex()]

    def convert_to_json(self):
        """Converts transactions to JSON format."""
        self.TxJson = []
        for tx in self.addTransactionsInBlock:
            self.TxJson.append(tx.to_dict())

    def calculate_fee(self):
        """Calculates the transaction fee by subtracting the total output amount from the total input amount."""
        self.input_amount = 0
        self.output_amount = 0
        """ Calculate Input Amount """
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

    def buildUTXOS(self):
        """uilds the list of unspent transactions by reading all transactions from the blocks in the blockchain."""
        allTxs = {}
        blocks = BlockchainDB().read()

        for block in blocks:
            for tx in block['Txs']:
                allTxs[tx['TxId']] = tx
            
        for block in blocks:
            for tx in block['Txs']:
                for txin in tx['tx_ins']:
                    if txin['prev_tx'] != "0000000000000000000000000000000000000000000000000000000000000000":
                        if len(allTxs[txin['prev_tx']]['tx_outs']) < 2:
                            del allTxs[txin['prev_tx']]
                        else:
                            txOut = allTxs[txin['prev_tx']]['tx_outs']
                            txOut.pop(txin['prev_index'])
        
        for tx in allTxs:
            self.utxos[tx] = Tx.to_obj(allTxs[tx])


    def settargetWhileBooting(self):
        """Sets the target difficulty and timestamp during blockchain boot-up."""
        bits, timestamp = self.getTargetDifficultyAndTimestamp()
        if bits is None or timestamp is None:
            print("Creating Genesis Block")
            return
        self.bits = bytes.fromhex(bits)
        self.current_target = bits_to_target(self.bits)

    def getTargetDifficultyAndTimestamp(self, BlockHeight = None):
        """Retrieves the target difficulty and timestamp from a specific block or the last block."""
        if BlockHeight:
            blocks = BlockchainDB().read()
            bits = blocks[BlockHeight]['BlockHeader']['bits']
            timestamp = blocks[BlockHeight]['BlockHeader']['timestamp']
        else:
            block = BlockchainDB().lastBlock()
            bits = block['BlockHeader']['bits']
            timestamp = block['BlockHeader']['timestamp']

        try:
            if not block:
                print("No previous block. A Genesis Block needs to be created.")
                return None, None
        except UnboundLocalError:
            pass

        return bits, timestamp


    def adjustTargetDifficulty(self, BlockHeight):
        if BlockHeight == 0:
            print("BlockHeight is 0. Skipping target difficulty adjustment.")
            return
        """Adjusts the target difficulty for every 10th block based on the average block mine time."""
        if BlockHeight % 10 == 0 and BlockHeight > 100:
            bits, timestamp = self.getTargetDifficultyAndTimestamp(BlockHeight - 10)
            Lastbits, lastTimestamp = self.getTargetDifficultyAndTimestamp()

            lastTarget = bits_to_target(bytes.fromhex(bits))
            AverageBlockMineTime = lastTimestamp - timestamp
            timeRatio = AverageBlockMineTime / AVERAGE_MINE_TIME

            NEW_TARGET = int(format(int(lastTarget * timeRatio)))

            if NEW_TARGET > MAX_TARGET:
                NEW_TARGET = MAX_TARGET
            
            self.bits = target_to_bits(NEW_TARGET)
            self.current_target = NEW_TARGET

    def BroadcastBlock(self, block):
        """Broadcasts a block to all nodes in the network."""
        self.startSync(block)

    def LostCompetition(self):
        """Handles the scenario of a miner losing the competition to add a block. It validates the block, removes spent transactions, and resolves conflicts between miners."""
        # Create a list to store blocks to be deleted
        deleteBlock = []
        # Create a temporary copy of the new blocks
        tempBlocks = dict(self.newBlockAvailable)

        # Iterate over each new block
        for newblock in tempBlocks:
            block = tempBlocks[newblock]
            # Add the block to the delete list
            deleteBlock.append(newblock)

            # Create a BlockHeader object from the block
            BlockHeaderObj = BlockHeader(block.BlockHeader.version,
                                block.BlockHeader.prevBlockHash, 
                                block.BlockHeader.merkleRoot, 
                                block.BlockHeader.timestamp,
                                block.BlockHeader.bits,
                                block.BlockHeader.nonce)

            # Validate the block
            if BlockHeaderObj.validateBlock():
                # Iterate over each transaction in the block
                for idx, tx in enumerate(block.Txs):
                    # Add the transaction to the UTXO set
                    self.utxos[tx.id()] = tx.serialize()
                    # Set the transaction ID
                    block.Txs[idx].TxId = tx.id()

                    # Delete spent transactions from the UTXO set
                    for txin in tx.tx_ins:
                        if txin.prev_tx.hex() in self.utxos:
                            del self.utxos[txin.prev_tx.hex()]

                    # Delete the transaction from the mempool
                    if tx.id() in self.MemPool:
                        del self.MemPool[tx.id()]

                    # Convert the transaction to a dictionary
                    block.Txs[idx] = tx.to_dict()
                # Convert the block header to hexadecimal                    
                block.BlockHeader.to_hex()
                # Write the block to the blockchain
                BlockchainDB().write([block.to_dict()])
            else:
                # Create dictionaries to store orphan and valid transactions
                orphanTxs = {}
                validTxs = {}
                # Check if there is a secondary chain
                if self.secondaryChain:
                    # Create a list to store blocks to be added
                    addBlocks = []
                    addBlocks.append(block)
                    prevBlockhash = block.BlockHeader.prevBlockHash.hex()
                    count = 0

                     # Iterate over the secondary chain
                    while count != len(self.secondaryChain):
                        if prevBlockhash in self.secondaryChain:
                            addBlocks.append(self.secondaryChain[prevBlockhash])
                            prevBlockhash = self.secondaryChain[prevBlockhash].BlockHeader.prevBlockHash.hex()
                        count += 1
                    
                    # Read the blockchain from the database
                    blockchain = BlockchainDB().read()
                    lastValidBlock = blockchain[-len(addBlocks)]

                    # Check if the last valid block is the previous block
                    if lastValidBlock['BlockHeader']['blockHash'] == prevBlockhash:
                        # Iterate over the blocks to be added
                        for i in range(len(addBlocks) - 1):
                            # Remove the last block from the blockchain
                            orphanBlock = blockchain.pop()

                            # Iterate over the transactions in the orphan block
                            for tx in orphanBlock['Txs']:
                                # Delete spent transactions from the UTXO set
                                if tx['TxId'] in self.utxos:
                                    del self.utxos[tx['TxId']]
                                    # Add the orphan transactions to the orphanTxs dictionary
                                    if tx['tx_ins'][0]['prev_tx'] != "0000000000000000000000000000000000000000000000000000000000000000":
                                        orphanTxs[tx['TxId']] = tx

                        # Update the blockchain in the database
                        BlockchainDB().update(blockchain)

                        # Iterate over the blocks to be added in reverse order                          
                        for Bobj in addBlocks[::-1]:
                            # Create a copy of the block
                            validBlock = copy.deepcopy(Bobj)
                            # Convert the block header to hexadecimal
                            validBlock.BlockHeader.to_hex()

                            # Iterate over the transactions in the block
                            for index, tx in enumerate(validBlock.Txs):
                                # Set the transaction ID
                                validBlock.Txs[index].TxId = tx.id()
                                # Add the transaction to the UTXO set
                                self.utxos[tx.id()] = tx

                                # Delete spent transactions from the UTXO set
                                for txin in tx.tx_ins:
                                    if txin.prev_tx.hex() in self.utxos:
                                        del self.utxos[txin.prev_tx.hex()]
                                
                                # Add the valid transactions to the validTxs dictionary
                                if tx.tx_ins[0].prev_tx.hex() != "0000000000000000000000000000000000000000000000000000000000000000":
                                    validTxs[validBlock.Txs[index].TxId] = tx

                                # Convert the transaction to a dictionary
                                validBlock.Txs[index] = tx.to_dict()
                            
                            # Write the valid block to the blockchain
                            BlockchainDB().write([validBlock.to_dict()])
                        
                        # Iterate over the orphan transactions
                        for TxId in orphanTxs:
                            # Add the orphan transactions to the mempool
                            if TxId not in validTxs:
                                self.MemPool[TxId] = Tx.to_obj(orphanTxs[TxId])

                # Add the block to the secondary chain
                self.secondaryChain[newblock] = block

        # Delete the blocks from the newBlockAvailable dictionary
        for blockHash in deleteBlock:
            del self.newBlockAvailable[blockHash]

    def addBlock(self, BlockHeight, prevBlockHash):
        """
    This function adds a new block to the blockchain. It first reads transactions from the memory pool,
    calculates the fee, and creates a coinbase transaction. It then adjusts the target difficulty and 
    mines the block. If the mining competition is lost, it calls the LostCompetition function. 
    Otherwise, it broadcasts the new block, removes spent transactions, stores UTXOs in cache, 
    converts transactions to JSON, and writes the block on disk.
        """
        # Read transactions from the memory pool
        self.read_transaction_from_memorypool()
        # Calculate the transaction fee
        self.calculate_fee()
        # Get the current timestamp
        timestamp = int(time.time())
        # Create a coinbase transaction
        coinbaseInstance = CoinbaseTx(BlockHeight)
        coinbaseTx = coinbaseInstance.CoinbaseTransaction()
        # Update the block size
        self.Blocksize += len(coinbaseTx.serialize())

        # Add the fee to the coinbase transaction
        coinbaseTx.tx_outs[0].amount = coinbaseTx.tx_outs[0].amount + self.fee

        # Add the coinbase transaction to the list of transaction IDs and transactions in the block
        self.TxIds.insert(0, bytes.fromhex(coinbaseTx.id()))
        self.addTransactionsInBlock.insert(0, coinbaseTx)

        # Calculate the merkle root of the transactions
        merkleRoot = merkle_root(self.TxIds)[::-1].hex()
        #Target difficulty currently doesn't work on empty blockchain
        self.adjustTargetDifficulty(BlockHeight)
        # Create a new block header
        blockheader = BlockHeader(
            VERSION, prevBlockHash, merkleRoot, timestamp, self.bits, nonce = 0
        )
         # Mine the block
        competitionOver = blockheader.mine(self.current_target, self.newBlockAvailable)

        # If the mining competition is lost
        if competitionOver:
            self.LostCompetition()
        else:
            # Create a new block
            newBlock = Block(BlockHeight, self.Blocksize, blockheader, len(self.addTransactionsInBlock),
                            self.addTransactionsInBlock)
            # Convert the block header to bytes
            blockheader.to_bytes()
            # Create a copy of the new block
            block = copy.deepcopy(newBlock)
            # Start a new process to broadcast the new block
            broadcastNewBlock = Process(target = self.BroadcastBlock, args = (block, ))
            broadcastNewBlock.start()
            # Convert the block header to hexadecimal
            blockheader.to_hex()
            # Remove spent transactions
            self.remove_spent_Transactions()
            # Remove transactions from the memory pool
            self.remove_transactions_from_memorypool()
            # Store unspent transaction outputs in cache
            self.store_uxtos_in_cache()
            # Convert transactions to JSON
            self.convert_to_json()

            print(
                f"Block {BlockHeight} mined successfully with Nonce value of {blockheader.nonce}"
            )
             # Write the block on disk
            self.write_on_disk(
                [
                    Block(
                        BlockHeight, self.Blocksize, blockheader.__dict__, len(self.TxJson), self.TxJson
                    ).__dict__
                ]
            )

    def main(self):
        """
    This is the main function that runs the blockchain. It fetches the last block and if it doesn't exist,
    it creates a genesis block. Then it enters an infinite loop where it fetches the last block, increments 
    the block height, and adds a new block to the blockchain.
        """
        # Fetch the last block from the blockchain
        lastBlock = self.fetch_last_block()
        # If the blockchain is empty, create a genesis block
        if lastBlock is None:
            self.GenesisBlock()

        # Start an infinite loop
        while True:
            # Fetch the last block from the blockchain
            lastBlock = self.fetch_last_block()
            # Increment the block height
            BlockHeight = lastBlock["Height"] + 1
            print(f"Current Block Height is is {BlockHeight}")
            # Get the hash of the previous block
            prevBlockHash = lastBlock["BlockHeader"]["blockHash"]
            # Add a new block to the blockchain
            self.addBlock(BlockHeight, prevBlockHash)
            
if __name__ == "__main__":
    
    # Read the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')
    localHost = config['DEFAULT']['host']
    localHostPort = int(config['MINER']['port'])
    simulateBTC = bool(config['MINER']['simulateBTC'])
    webport = int(config['WEBHOST']['port'])

    # Create shared dictionaries for the manager
    with Manager() as manager:
        utxos = manager.dict()
        MemPool = manager.dict()
        newBlockAvailable = manager.dict()
        secondaryChain = manager.dict()
        
        # Start the web application process
        webapp = Process(target=main, args=(utxos, MemPool, webport, localHostPort))
        webapp.start()
        
        # Create a sync manager and start the server process
        sync = syncManager(localHost, localHostPort, newBlockAvailable, secondaryChain, MemPool)
        startServer = Process(target = sync.spinUpTheServer)
        startServer.start()

        # Create a blockchain and start the synchronization process
        blockchain = Blockchain(utxos, MemPool, newBlockAvailable, secondaryChain)
        blockchain.startSync()
        blockchain.buildUTXOS()

        # If the simulation of Bitcoin is enabled, start the auto broadcast process
        if simulateBTC:
            autoBroadcastTxs = Process(target = autoBroadcast)
            autoBroadcastTxs.start()

        # Set the target while booting and start the main function of the blockchain
        
        blockchain.settargetWhileBooting()
        blockchain.main()
    