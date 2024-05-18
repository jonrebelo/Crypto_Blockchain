from flask import Flask, render_template, request
from Blockchain.client.send_crypto import send_crypto

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])

def wallet():
    message = ''
    if request.method == 'POST':
        from_address = request.form.get('fromAddress')
        to_address = request.form['toAddress']
        Amount = request.form.get("Amount", type = int)
        send_coin = send_crypto(from_address, to_address, Amount, UTXOS)


        if not send_coin.prepare_transaction():
            message = "Insufficient balance"
        
    return render_template('wallet.html', message = message)

def main(utxos):
    global UTXOS
    UTXOS = utxos
    app.run()
