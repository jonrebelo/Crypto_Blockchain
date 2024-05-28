from Blockchain.Backend.util.util import hash256, little_endian_to_int, int_to_little_endian

class BlockHeader:
    def __init__(self, version, prev_block_hash, merkleRoot, timestamp, bits):
        self.version = version
        self.prev_block_hash = prev_block_hash
        self.merkleRoot = merkleRoot
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = 0
        self.blockHash = ''

    def serialize(self):
        result = int_to_little_endian(self.version, 4)
        result += self.prev_block_hash[::-1]
        result += self.merkleRoot[::-1]
        result += int_to_little_endian(self.timestamp, 4)
        result += self.bits
        result += self.nonce
        return result 

    def mine(self, target):
        self.blockHash = target + 1
        #Check blockHash for leading 0s
        while self.blockHash > target:
            self.blockHash = little_endian_to_int(hash256(int_to_little_endian(self.version, 4)
                        + bytes.fromhex(self.prev_block_hash)[::-1]
                        + bytes.fromhex(self.merkleRoot)
                        + int_to_little_endian(self.timestamp, 4)
                        + self.bits
                        + int_to_little_endian(self.nonce, 4)
                )
            )
            self.nonce += 1
            print(f"Mining Started {self.nonce}", end = '\r')
        self.blockHash = int_to_little_endian(self.blockHash, 32).hex()[::-1]
        self.bits = self.bits.hex()