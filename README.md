# Cryptocurrency Blockchain

This project is a cryptocurrency blockchain, similar to Bitcoin, implemented using the SHA256 algorithm. 

## Features

- **SHA256 Algorithm**: The blockchain uses the SHA256 algorithm for hashing.
- **Proof of Work (PoW) Mining**: The blockchain implements a PoW algorithm for mining new blocks.
- **Public Nodes**: The network consists of public nodes that participate in the blockchain.
- **Flask User Interface**: A Flask application is used as a user interface for sending and receiving transactions.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.6 or higher
- Flask

### Installing

Clone the repository to your local machine:

```bash
git clone https://github.com/jonrebelo/Crypto_Blockchain.git
```

### Environment

```bash
conda create --name blockchain_apps charset-normalizer click colorama flask idna itsdangerous jinja2 markupsafe pillow pycryptodome qrcode requests urllib3 werkzeug
conda activate blockchain_apps
pip install flask-qrcode
```
### Instructions

1. Run blockchain.py
2. A flask server will spinup at 127.0.0.1:5900 (This can be changed in the config.ini if desired)
3. Mining will begin 
4. Navigate to 127.0.0.1:5900 in your browser to launch block explorer.
5. Transactions can be sent from the Wallet page. Check account file in the data folder for public addresses that have already been generated. 
6. Unconfirmed Transactions can be found in the Mempool page.
7. Mining will continue until the process is stopped.

If you want to generate your own private key and address:

1. With environment activated, run account.py.
2. The terminal will give you private and public keys. This will be recorded in the account file in the data folder. You can run account.py multiple times to generate multiple keys and addresses.
3. Go to Tx.py and replace the MINER_ADDRESS with your public address and PRIVATE_KEY with your private key. This will ensure mined units end up in your new wallet.

### Blockchain Functionality:

1. How does adding a block to the blockchain work?

![Image description](./Charts/addBlock.png)

Read transactions from memory pool: Gather transactions waiting to be added to the blockchain.

Calculate transaction fee: Determine the fee associated with including transactions in the block.

Get current timestamp: Obtain the current time to timestamp the block.

Create coinbase transaction: Generate a special transaction, called the coinbase transaction, which rewards the miner with newly minted cryptocurrency.

Update block size: Adjust the block size to accommodate the coinbase transaction.

Add fee to coinbase transaction: Incorporate the transaction fee into the coinbase transaction.

Add coinbase transaction to block: Include the coinbase transaction in the block.

Calculate Merkle root of transactions: Compute a cryptographic hash of all transactions in the block to create the Merkle root.

Create block header: Formulate a block header containing metadata such as version, previous block hash, Merkle root, timestamp, and other parameters.

Mine the block: Perform the proof-of-work process to find a suitable nonce that satisfies the difficulty target.

Create a new block: Assemble all components (block header, transactions, etc.) into a new block.

Convert block header to bytes: Convert the block header into a format suitable for storage or transmission.

Create a copy of the new block: Make a copy of the newly created block.

Start a new process to broadcast the new block: Initiate a process to disseminate the newly mined block to other nodes in the network.

Remove spent transactions: Eliminate transactions that have been included in the block from the list of unspent transactions.

Remove transactions from memory pool: Clear the memory pool of transactions that have been added to the block.

Store unspent transaction outputs in cache: Maintain a record of unspent transaction outputs for future reference.

Convert transactions to JSON: Serialize transactions into JSON format for storage or transmission.

 Write the block on disk: Persist the newly mined block onto the blockchain ledger by writing it to disk.
 
 2. How does the Mempool work?

 ![Image description](./Charts/mempool.png)

 In a blockchain network, the mempool serves as a temporary storage space for pending transactions before they are included in a block and added to the blockchain. Here's how this specific mempool works:

Start: The process begins.

Read Database: The system reads the blockchain database to gather information about existing blocks.

Manage Memory Pool (Mempool): Transactions are managed within the mempool, where they await processing.

Store UTXOs in Cache: Unspent Transaction Outputs (UTXOs) are stored in a cache for quick reference during transaction processing.

Remove Spent Transactions: Transactions that have been included in blocks and spent are removed from the UTXO set.

Check for Double Spending Attempt: The system checks if any transaction in the mempool is attempting to spend the same UTXO more than once, which would indicate a double spending attempt.

Read Transactions from Memory Pool: Pending transactions are read from the mempool, and potential double spending attempts are filtered out.

Remove Transactions from Memory Pool: Processed transactions are removed from the mempool, as they have been included in blocks and are no longer pending.

End: The process concludes.

The mempool plays a crucial role in maintaining the integrity and efficiency of the blockchain network by ensuring that valid transactions are processed and added to the blockchain in a timely manner, while preventing double spending and other fraudulent activities.
