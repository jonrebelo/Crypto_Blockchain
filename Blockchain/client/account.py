import sys
sys.path.append('F:/00_Github/Crypto_Blockchain')
from Blockchain.Backend.core.EllepticCurve.EllepticCurve import Sha256Point
from Blockchain.Backend.util.util import hash160, hash256
import secrets


#create a Bitcoin Address

class account:
    def createKeys(self):
        #constants in our elliptical curve formula in hex
        Gx = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
        Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8

        G = Sha256Point(Gx, Gy)

        private_key = secrets.randbits(256)
        uncompressed_public_key = private_key * G
        x_point = uncompressed_public_key.x
        y_point = uncompressed_public_key.y

        #define the prefix of the public key. Written in bytes. big refers to "big endian" which writes the code from left to right. little would be the opposite. Then create public key
        if y_point.num % 2 == 0:
            compressed_key = b'\x02' + x_point.num.to_bytes(32, 'big')
        else:
            compressed_key = b'\x03' + x_point.num.to_bytes(32, 'big')

        #convert public key to public address
        v_hash160 = hash160(compressed_key)
        """Prefix for Mainnet"""
        main_prefix = b'\x00'

        new_address = main_prefix + v_hash160

        #Verifying address is valid for sending transactions
        """"Checksum"""
        checksum = hash256(new_address)[:4]

        new_address = new_address + checksum

        BASE58_AlPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

        count = 0

        for c in new_address:
            if c == 0:
                count +=1
            else:
                break
        num = int.from_bytes(new_address, 'big')
        prefix = '1' * count

        result = ''

        while num > 0:
            #num gets divided by 58, so it's always less than 58
            num, mod = divmod(num, 58)
            #assigns values from BASE58 until complete and assigns to result variable
            result = BASE58_AlPHABET[mod] + result

        public_address = prefix + result

        print(f"Private key is {private_key}")
        print(f"Public Address is {public_address}")

if __name__ == '__main__':
    acct = account()
    acct.createKeys()