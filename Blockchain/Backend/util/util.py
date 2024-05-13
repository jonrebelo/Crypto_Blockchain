import hashlib

def hash256(s):
    """Two passes of SHA 256"""
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()