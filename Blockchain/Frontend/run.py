from flask import Flask, render_template, request, redirect, url_for
from Blockchain.client.send_crypto import send_crypto
from Blockchain.Backend.core.Tx import Tx
from Blockchain.Backend.core.database.database import BlockchainDB
from Blockchain.Backend.util.util import encode_base58, decode_base58, sha256

app = Flask(__name__)
main_prefix = b'\x00'


@app.route('/')
def index():
    return render_template('/home.html')

@app.route('/transactions')
def transactions(): 
    return "<h1>Transactions</h1>"

@app.route('/mempool')
def mempool(): 
    return "<h1>MemPool</h1>"

@app.route('/search')
def search(): 
    return "<h1>Search</h1>"

""" Read data from the Blockchain """
def readDatabase():
    ErrorFlag = True
    while ErrorFlag:
        try:
            blockchain = BlockchainDB()
            blocks = blockchain.read()
            print("Blocks from database:", blocks)  # print blocks
            ErrorFlag = False
        except:
            ErrorFlag = True
            print("Error reading database")
    return blocks

@app.route('/block')
def block():
    if request.args.get('blockHeader'):
        return redirect(url_for('showBlock', blockHeader=request.args.get('blockHeader')) )
    else:
        blocks = readDatabase()
        return render_template('block.html', blocks = blocks)

@app.route('/block/<blockHeader>')
def showBlock(blockHeader):
    blocks = readDatabase()
    for block in blocks:
        if block['BlockHeader']['blockHash'] == blockHeader:
            return render_template('block_details.html', block = block, main_prefix = main_prefix, 
            encode_base58 = encode_base58, bytes = bytes, sha256 = sha256)
    
    return "<h1> Invalid Identifier </h1>"

@ app.route('/address')
def address():
    return "<h1> Address Page </h1>"

@app.route("/wallet", methods=['GET', 'POST'])
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