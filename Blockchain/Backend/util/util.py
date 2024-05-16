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

