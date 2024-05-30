import requests
import time
import random
from Blockchain.Backend.core.database.database import AccountDB

fromAccount = "1LHVXFSmNTPd3wKgjrZKeYwoesyPqaaGnd"

""" Read all the accounts """
AllAccounts = AccountDB().read()

def autoBroadcast():
    while True:
        for account in AllAccounts:
            if account["PublicAddress"] != fromAccount:
                paras = {"fromAddress": fromAccount,
                        "toAddress": account["PublicAddress"],
                        "Amount": random.randint(1,35)}

                res = requests.post(url ="http://localhost:5900/wallet", data = paras)   
        time.sleep(3)