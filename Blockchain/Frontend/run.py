from flask import Flask, render_template, request
from Blockchain.client.send_crypto import send_crypto
from Blockchain.Backend.core.Tx import Tx

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])

def wallet():
    message = ''
    if request.method == 'POST':
        from_address = request.form.get('from_address')
        to_address = request.form['to_address']
        Amount = request.form.get("Amount", type = int)
        send_coin = send_crypto(from_address, to_address, Amount, UTXOS)
        tx_obj =  send_coin.prepare_transaction()

        script_pub_key = send_coin.script_pub_key(from_address)
        verified = True

        #verify all transactions are valid before entering intot the mempool
        if not tx_obj:
            message = "Invalid Transaction"

        if isinstance(tx_obj, Tx):
            for index, tx in enumerate(tx_obj.tx_ins):
                if not tx_obj.verify_input(index, script_pub_key):
                    verified = False
            
            if verified:
                MEMPOOL[tx_obj.TxId] = tx_obj
                message = "Transaction added to mempool"
        
    return render_template('wallet.html', message = message)

def main(utxos, MemPool):
    global UTXOS
    global MEMPOOL
    UTXOS = utxos
    MEMPOOL = MemPool
    app.run()
