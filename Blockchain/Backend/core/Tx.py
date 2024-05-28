from Blockchain.Backend.core.script import Script
from Blockchain.Backend.util.util import int_to_little_endian, bytes_needed, decode_base58, little_endian_to_int, encode_varint, hash256





zero_hash = b"\0" * 32
reward = 50

miner_private_key = '49190780511027130330696391407676493615547676779410269489938157581909610769221'
miner_address = '1LHVXFSmNTPd3wKgjrZKeYwoesyPqaaGnd'
sig_hash_all = 1


class Coinbase_Tx:
    """Miner reward transaction. Base because there is no sender, it comes from a block reward.
    Would be the first transaction of every block. Has nothing to do with coinbase company"""
    def __init__(self, block_height):
        self.block_height_in_little_endian = int_to_little_endian(block_height, bytes_needed(block_height))
    
    def Coinbase_Transaction(self):
        prev_tx = zero_hash
        prev_index = 0xffffffff

        tx_ins = []
        tx_ins.append(Tx_In(prev_tx, prev_index))
        tx_ins[0].script_sig.cmds.append(self.block_height_in_little_endian)

        tx_outs = []
        target_amount = reward * 100000000
        target_h160 = decode_base58(miner_address)
        target_script = Script.p2pkh_script(target_h160)
        tx_outs.append(Tx_Out(amount = target_amount, script_pubkey= target_script))
        coin_base_tx = Tx(1, tx_ins, tx_outs, 0)
        coin_base_tx.TxId = coin_base_tx.id()

        return coin_base_tx

class Tx:
    """
    The Tx class represents a transaction in the blockchain.
    """
    def __init__(self, version, tx_ins, tx_outs, locktime):
        """
        Initialize a new transaction.

        :param version: The version of the transaction format.
        :param tx_ins: A list of transaction inputs.
        :param tx_outs: A list of transaction outputs.
        :param locktime: The time when the transaction becomes valid.
        """
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime
    
    def id(self):
        """Readable Tx ID"""
        return self.hash().hex()

    def hash(self):
        """Return the hash of the transaction. Reverse Order [::-1]"""
        return hash256(self.serialize())[::-1]

    def serialize(self):
        """Convert Tx inputs into byte format"""
        #Convert version to little endian
        result = int_to_little_endian(self.version, 4)

        #Check how many transaction inputs there are
        result+= encode_varint(len(self.tx_ins))

        #Loop through all transaction inputs
        for tx_in in self.tx_ins:
            result += tx_in.serialize()

        #Same for transaction outputs
        result += encode_varint(len(self.tx_outs))
        
        for tx_out in self.tx_outs:
            result += tx_out.serialize()

        #Convert locktime to little endian
        result += int_to_little_endian(self.locktime, 4)

        return result
    
    def sig_hash(self, input_index, script_pubkey):
        """Convert inputs into bytes and hash them"""
        s = int_to_little_endian(self.version, 4)
        s += encode_varint(len(self.tx_ins))

        for i, tx_in in enumerate(self.tx_ins):
            if i == input_index:
                s += Tx_In(tx_in.prev_tx, tx_in.prev_index, script_pubkey).serialize()
            else:
                s += Tx_In(tx_in.prev_tx, tx_in.prev_index).serialize()

        s += encode_varint(len(self.tx_outs))

        for tx_out in self.tx_outs:
            s += tx_out.serialize()

        s += int_to_little_endian(self.locktime, 4)
        s += int_to_little_endian(sig_hash_all, 4)

        h256 = hash256(s)
        return int.from_bytes(h256, 'big')

    
    def sign_input(self, input_index, private_key, script_pubkey):
        """Sign the input using the private key"""
        z = self.sig_hash(input_index, script_pubkey)
        der = private_key.sign(z).der()
        sig = der + sig_hash_all.to_bytes(1, 'big')
        sec = private_key.point.sec()
        self.tx_ins[input_index].script_sig = Script([sig, sec])

    def verify_input(self, input_index, script_pubkey):
        """Verify the input using the public key"""
        tx_in = self.tx_ins[input_index]
        z = self.sig_hash(input_index, script_pubkey)
        combined = tx_in.script_sig + script_pubkey
        return combined.evaluate(z)
    

    def is_coinbase(self):
        """
        Check there is exactly 1 input
        - Get 1st input and check is prev_tx is b'\x00 * 32
        - Check first input prev_index is 0xffffffff
        """

        if len(self.tx_ins) != 1:
            return False
        
        first_input = self.tx_ins[0]

        if first_input.prev_tx != b'\x00' * 32:
            return False
        
        if first_input.prev_index != 0xffffffff:
            return False
        
        return True
    
    @classmethod
    def to_obj(cls, item):
        """
    Class method to convert a dictionary representation of a transaction into a `Tx` object.

    The method iterates over the 'tx_ins' and 'tx_outs' lists in the dictionary, converting each transaction input and output into a `Tx_In` and `Tx_Out` object respectively.

    For each transaction input, the method creates a list of commands by iterating over the 'cmds' list in the 'script_sig' dictionary. 
    If the 'prev_tx' value is a string of 64 zeroes, the command is converted from an integer to a little-endian byte string. 
    Otherwise, if the command is an integer, it is appended as is, and if it's a hexadecimal string, it's converted to bytes and appended.

    For each transaction output, the method creates a list of commands by iterating over the 'cmds' list in the 'script_pubkey' dictionary. 
    If the command is an integer, it is appended as is, and if it's a hexadecimal string, it's converted to bytes and appended.

    The method then creates a `Tx` object with the lists of `Tx_In` and `Tx_Out` objects and returns it.
    """
        TxInList = []
        TxOutList = []
        cmds = []

        for tx_in in item['tx_ins']:
            for cmd in tx_in['script_sig']['cmds']:
               
                if tx_in['prev_tx'] == "0000000000000000000000000000000000000000000000000000000000000000":
                    cmds.append(int_to_little_endian(int(cmd), bytes_needed(int(cmd))))
                else:
                    if type(cmd) == int:
                        cmds.append(cmd)
                    else:
                        cmds.append(bytes.fromhex(cmd))
            TxInList.append(Tx_In(bytes.fromhex(tx_in['prev_tx']),tx_in['prev_index'],Script(cmds)))   

        
        cmdsout = []
        for tx_out in item['tx_outs']:
            for cmd in tx_out['script_pubkey']['cmds']:
                if type(cmd) == int:
                    cmdsout.append(cmd)
                else:
                    cmdsout.append(bytes.fromhex(cmd))
                    
            TxOutList.append(Tx_Out(tx_out['amount'],Script(cmdsout)))
            cmdsout= []
        
        return cls(1, TxInList, TxOutList, 0)
    
    
    def to_dict(self):
        """
        Convert Transaction
        - Convert prev_tx Hash in hex from bytes
        - Convert block_height in hex from Script signature
        """

        for tx_index, tx_in, in enumerate(self.tx_ins):
            if self.is_coinbase():
                tx_in.script_sig.cmds[0] = little_endian_to_int(tx_in.script_sig.cmds[0])
            
            tx_in.prev_tx = tx_in.prev_tx.hex()

            for index, cmd in enumerate(tx_in.script_sig.cmds):
                if isinstance(cmd, bytes):
                    tx_in.script_sig.cmds[index] = cmd.hex()
            
            tx_in.script_sig = tx_in.script_sig.__dict__
            self.tx_ins[tx_index] = tx_in.__dict__

        """
        Convert Transaction Output to Dictionary
        - If there are numbers, nothing is needed
        - If there are bytes, convert to hex
        - Loop through all Tx_Outs and convert to dictionary
        """
        for index, tx_out in enumerate(self.tx_outs):
            tx_out.script_pubkey.cmds[2] = tx_out.script_pubkey.cmds[2].hex()
            tx_out.script_pubkey = tx_out.script_pubkey.__dict__
            self.tx_outs[index] = tx_out.__dict__

        return self.__dict__
       



class Tx_In:
    """
    The Tx_In class represents a transaction input.
    """
    def __init__(self, prev_tx, prev_index, script_sig = None, sequence = 0xffffffff):
        """
        Initialize a new transaction input.

        :param prev_tx: The hash of the previous transaction.
        :param prev_index: The index of the specific output in the previous transaction.
        :param script_sig: The script that unlocks the previous output.
        :param sequence: The sequence number.
        """
        self.prev_tx = prev_tx
        self.prev_index = prev_index

        if script_sig is None:
            self.script_sig = Script()
        else:
            self.script_sig = script_sig

        self.sequence = sequence

    def serialize(self):
        """Convert Tx inputs into byte format"""
        result = self.prev_tx[::-1]
        result += int_to_little_endian(self.prev_index, 4)
        result += self.script_sig.serialize()
        result += int_to_little_endian(self.sequence, 4)
        return result

class Tx_Out:
    """
    The Tx_Out class represents a transaction output.
    """
    def __init__(self, amount, script_pubkey):
        """
        Initialize a new transaction output.

        :param amount: The amount of cryptocurrency for this output.
        :param script_pubkey: The script that locks the output.
        """
        self.amount = amount
        self.script_pubkey = script_pubkey

    def serialize(self):
        """Convert Tx inputs into byte format"""
        result = int_to_little_endian(self.amount, 8)
        result += self.script_pubkey.serialize()
        return result
