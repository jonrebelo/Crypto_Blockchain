from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.util.util import int_to_little_endian, little_endian_to_int, encode_varint, read_varint
from Blockchain.Backend.core.Tx import Tx

class Block:
    """
    Block is a storage container that stores transactions. It represents a block in a blockchain.
    """
    command = b'block'

    def __init__(self, Height, Blocksize, BlockHeader, TxCount, Txs):
        """
        Initialize a Block instance with height, block size, block header, transaction count, and transactions.
        """
        self.Height = Height
        self.Blocksize = Blocksize
        self.BlockHeader = BlockHeader
        self.Txcount = TxCount
        self.Txs = Txs

    @classmethod
    def parse(cls, s):
        """
        Parse a stream of bytes into a Block instance.
        """
        Height = little_endian_to_int(s.read(4))
        BlockSize = little_endian_to_int(s.read(4))
        blockHeader = BlockHeader.parse(s)
        numTxs = read_varint(s)

        Txs = []

        for _ in range(numTxs):
            Txs.append(Tx.parse(s))

        return cls(Height, BlockSize, blockHeader, numTxs, Txs)
        
    def serialize(self):
        """
        Serialize the Block instance into a stream of bytes.
        """
        result = int_to_little_endian(self.Height, 4)
        result += int_to_little_endian(self.Blocksize, 4)
        result += self.BlockHeader.serialize()
        result += encode_varint(len(self.Txs))

        for tx in self.Txs:
            result += tx.serialize()
        
        return result 

    @classmethod
    def to_obj(cls, lastblock):
        """
        Convert the Block instance into a dictionary representation.
        """
        block = BlockHeader(lastblock['BlockHeader']['version'],
                    bytes.fromhex(lastblock['BlockHeader']['prevBlockHash']),
                    bytes.fromhex(lastblock['BlockHeader']['merkleRoot']),
                    lastblock['BlockHeader']['timestamp'],
                    bytes.fromhex(lastblock['BlockHeader']['bits']))
        
        block.nonce = int_to_little_endian(lastblock['BlockHeader']['nonce'], 4)

        Transactions = []
        for tx in lastblock['Txs']:
            Transactions.append(Tx.to_obj(tx))
        
        block.BlockHash = bytes.fromhex(lastblock['BlockHeader']['blockHash'])
        return cls(lastblock['Height'], lastblock['Blocksize'], block, len(Transactions), Transactions)

    def to_dict(self):
        dt = self.__dict__
        self.BlockHeader = self.BlockHeader.to_dict()
        return dt