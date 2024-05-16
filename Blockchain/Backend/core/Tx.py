from Blockchain.Backend.core.script import Script
from Blockchain.Backend.util.util import int_to_little_endian, bytes_needed, decode_base58, little_endian_to_int





zero_hash = b'\0' * 32
reward = 50

miner_private_key = '51256644610767104174880828410988796911200594082524157987306154111069280366397'
miner_address = '1JzV4Su53uenm6Jimij7RCdfquJRMSu4HA'

class Coinbase_Tx:
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

        return Tx(1, tx_ins, tx_outs, 0)

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
    
    def to_dict(self):
        """
        Convert Coinbase Transaction
        - Convert prev_tx Hash in hex from bytes
        - Convert block_height in hex from Script signature
        """

        if self.is_coinbase():
            self.tx_ins[0].prev_tx = self.tx_ins[0].prev_tx.hex()
            self.tx_ins[0].script_sig.cmd[0] = little_endian_to_int(self.tx_ins[0].script_sig.cmds[0])
            self.tx_ins[0].script_sig = self.tx_ins[0].script_sig.__dict__

        self.tx_ins[0] = self.tx_ins[0].__dict__

        """
        Convert Transaction Output to Dictionary
        - If there are numbers, nothing is needed
        - If there are bytes, convert to hex
        - Loop through all Tx_Outs and convert to dictionary
        """
        self.tx_outs[0].script_pubkey.cmds[2] = self.tx_outs[0].script_pubkey.cmds[2].hex()
        self.tx_outs[0].script_pubkey = self.tx_outs[0].script_pubkey.__dict__
        self.tx_outs[0] = self.tx_outs[0].__dict__

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
