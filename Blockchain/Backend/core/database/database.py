import os
import json

#base Class
class BaseDB:
    def __init__(self):
        self.basepath = "data"
        self.filepath = "/".join((self.basepath, self.filename))

# Function to read data
    def read(self):
        if not os.path.exists(self.filepath):
            print(f"File {self.filepath} not available")
            return False
        
        with open(self.filepath, "r") as file:
            raw = file.readline()

# If no data (Genesis block) create empty data file
        if len(raw) > 0:
            data = json.loads(raw)    
        else:
            data = []
        return data
    
#Append data with new block
    def write(self, item):
        data = self.read()
        if data:
            data = data + item
        else:
            data = item
       
        with open(self.filepath, "w+") as file:
            file.write(json.dumps(data))


#subclass of BaseDB. Where blockchain history will be stored.
class BlockchainDB(BaseDB):
    def __init__(self):
        self.filename = "blockchain"
        super().__init__()

    def lastBlock(self):
        data = self.read()

        if data:
            return data[-1]
