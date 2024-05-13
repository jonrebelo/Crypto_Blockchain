from Blockchain.Backend.util.util import hash256

class BlockHeader:
    def __init__(self, version, PrevBlockHash, merkleRoot, timestamp, bits):
        self.version = version
        self.PrevBlockHash = PrevBlockHash
        self.merkleRoot = merkleRoot
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = 0
        self.blockHash = ''

    def mine(self):
        while (self.blockHash[0:4]) != '0000':
            #combine and pass into hash function. converts non-strings into strings, then convert to hex.
            self.blockHash = hash256((str(self.version) + self.PrevBlockHash + self.merkleRoot + str(self.timestamp)
                    + self.bits + str(self.nonce)).encode()).hex