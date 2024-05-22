import hashlib
from Crypto.Hash import RIPEMD160
from hashlib import sha256
from math import log
from Blockchain.Backend.core.EllepticCurve.EllepticCurve import BASE58_ALPHABET

def hash256(s):
    """Two passes of SHA 256"""
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def hash160(s):
    return RIPEMD160.new(sha256(s).digest()).digest()

def int_to_little_endian(n, length):
    """int_to_little_endian takes an integer and return the little-endian byte sequence of length"""
    return n.to_bytes(length, 'little')

def little_endian_to_int(b):
    """little_endian_to_int takes byte sequence and returns the integer"""
    return int.from_bytes(b, 'little')

def bytes_needed(n):
    #calculate how many bytes it takes to store an integer
    if n == 0:
        return 1
    return int(log(n, 256)) + 1

def decode_base58(s):
    num = 0

    for c in s:
        num *= 58
        num += BASE58_ALPHABET.index(c)
    
    combined = num.to_bytes(25, byteorder='big')
    checksum = combined[-4:]

    if hash256(combined[:-4])[:4] != checksum:
        raise ValueError(f'invalid address {checksum} {hash256(combined[:-4])[:4]}')
    
    return combined[1:-4]

def encode_varint(i):
    """Enncodes integers as a varint
    Determines the amount of bytes required to represent a hexical number"""
    if i < 0xfd:
        return bytes([i])
    elif i < 0x10000:
        return b'\xfd' + int_to_little_endian(i, 2)
    elif i < 0x100000000:
        return b'\xfe' + int_to_little_endian(i, 4)
    elif i < 0x10000000000000000:
        return b'\xff' + int_to_little_endian(i, 8)
    else:
        raise ValueError(f'integer too large: {i}')
    
def merkle_parent_level(hashes):
    """Takes a list of binary hashes and returns a list that is half the length"""

    if len(hashes) % 2 == 1:
        hashes.append(hashes[-1])
    
    parent_level = []
    for i in range(0, len(hashes), 2):
        parent = hash256(hashes[i] + hashes[i + 1])
        parent_level.append(parent)
    
    return parent_level
    
def merkle_root(hashes):
    """
    Takes a list of binary hashes and returns the Merkle root.

    The Merkle root is the hash of all the hashes of all the transactions in a block in a blockchain. 
    It is created by hashing together pairs of TXIDs, which gives you a list of hashes. 
    Then you hash together pairs of these hashes and so on until you end up with a single hash - the Merkle root.

    Parameters:
    hashes (list): A list of binary hashes of the transactions in a block.

    Returns:
    str: The Merkle root of the hashes.

    """

    current_level = hashes
    #Because merkle_root is the final hash, we need to loop through the hashes until we have only one hash left
    while len(current_level) > 1:
        current_level = merkle_parent_level(current_level)

    return current_level[0]

def target_to_bits(target):
    """
    Converts a target integer into a compact representation called 'bits'.

    This function is used in Bitcoin's difficulty adjustment algorithm. The 'bits' 
    format is a compact representation of a target, which is a 256-bit number that 
    a hashed block header must be less than or equal to for new blocks to be accepted.

    Parameters:
    target (int): The target value to be converted into 'bits'.

    Returns:
    bytes: The 'bits' representation of the target.

    Steps:
    1. Convert the target integer into bytes using big endian byte order.
    2. Remove any leading zeros from the byte representation of the target.
    3. If the first byte is greater than 127 (0x7F), increment the length of the byte string by 1 and 
       take the first two bytes as the coefficient. Otherwise, the length of the byte string is the exponent 
       and the first three bytes are the coefficient.
    4. The 'bits' are then calculated by concatenating the reversed coefficient and the exponent.
    """

    raw_bytes = target.to_bytes(32, "big")
    raw_bytes = raw_bytes.lstrip(b"\x00")  # Remove leading zeros

    if raw_bytes[0] > 0x7F:  # If the first byte is greater than 127
        exponent = len(raw_bytes) + 1
        coefficient = b"\x00" + raw_bytes[:2]
    else:
        exponent = len(raw_bytes)
        coefficient = raw_bytes[:3]

    new_bits = coefficient[::-1] + bytes([exponent])  # Calculate 'bits'

    return new_bits