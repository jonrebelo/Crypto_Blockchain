from Blockchain.Backend.util.util import decode_base58
from Blockchain.Backend.core.script import Script
from Blockchain.Backend.core.Tx import Tx_In, Tx_Out, Tx
from Blockchain.Backend.core.database.database import AccountDB
from Blockchain.Backend.core.EllepticCurve.EllepticCurve import PrivateKey
import time

class send_crypto:
    #initialize the class
    #from_account: the public address of the sender
    #to_account: the public address of the receiver
    #amount: the amount of cryptocurrency to be sent
    #utxos: the unspent transaction outputs
    def __init__(self, from_account, to_account, amount, utxos):
        self.coin = 100000000
        self.from_public_address = from_account
        self.to_account = to_account
        self.amount = amount * self.coin
        self.utxos = utxos

    #Decode the public address
    def script_pub_key(self, public_address):
        h160 = decode_base58(public_address)
        script_pub_key = Script.p2pkh_script(h160)
        return script_pub_key
    
    def get_private_key(self):
        all_accounts = AccountDB().read()
        for account in all_accounts:
            if account["public_address"] == self.from_public_address:
                return account["private_key"]
    
    #Prepare the transaction inputs
    def prepare_tx_in(self):
        tx_ins = []
        self.total = 0

        """Convert Public address into Public Hash to find tx_outs locked to this hash"""

        self.from_address_script_pub_key = self.script_pub_key(self.from_public_address)
        self.from_pub_key_hash = self.from_address_script_pub_key.cmds[2]

        new_utxos = {}

        try:
            while len(new_utxos) < 1:
                new_utxos = dict(self.utxos)
                time.sleep(2)
        except Exception as e:
            print (f"Error in converting the Managed Dicctionary to Normal Dictionary")

        #Iterate through the unspent transaction outputs
        for tx_byte in new_utxos:
            if self.total < self.amount:
                tx_obj = new_utxos[tx_byte]


                for index, tx_out in enumerate(tx_obj.tx_outs):
                    if tx_out.script_pubkey.cmds[2] == self.from_pub_key_hash:
                        self.total += tx_out.amount
                        prev_tx = bytes.fromhex(tx_obj.id())
                        tx_ins.append(Tx_In(prev_tx, index))
            else:
                break
            #Check if the total amount is less than the amount to be sent
        self.sufficient_balance = True
        if self.total < self.amount:
            self.sufficient_balance = False

        return tx_ins            

    #Prepare the transaction outputs
    def prepare_tx_out(self):
        tx_outs = []
        to_script_pub_key = self.script_pub_key(self.to_account)
        tx_outs.append(Tx_Out(self.amount, to_script_pub_key))

        """Fee Calculation"""
        self.fee = self.coin

        #calculate change
        self.change_amount = self.total - self.amount - self.fee

        #send change back to the sender
        tx_outs.append(Tx_Out(self.change_amount, self.from_address_script_pub_key))
        return tx_outs
    
    def sign_tx(self):
        secret = self.get_private_key()
        priv = PrivateKey(secret = secret)

        for index, input in enumerate(self.tx_ins):
            self.tx_obj.sign_input(index, priv, self.from_address_script_pub_key)

        return True



    def prepare_transaction(self):
        self.tx_ins = self.prepare_tx_in()

        if self.sufficient_balance:
            self.tx_outs = self.prepare_tx_out()
            self.tx_obj = Tx(1, self.tx_ins, self.tx_outs, 0)
            self.tx_obj.TxId = self.tx_obj.id()
            self.sign_tx()
            return self.tx_obj
        
        return False

