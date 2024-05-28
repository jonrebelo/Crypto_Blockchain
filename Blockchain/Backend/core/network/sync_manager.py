from Blockchain.Backend.core.network.connection import Node
from Blockchain.Backend.core.database.database import BlockchainDB
from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.core.block import Block
from Blockchain.Backend.core.network.network import request_block, network_envelope, finished_sending
from Blockchain.Backend.core.Tx import Tx
from threading import Thread


class sync_manager:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def spinup(self):
        self.server = Node(self.host, self.port)
        self.server.start_server()
        print(f" [Server started] \n Listening for connections at {self.host}:{self.port} \n")

        while True:
            self.conn, self.addr = self.server.accept_connection()
            handle_conn = Thread(target = self.handle_connection)
            handle_conn.start()

    def handle_connection(self):
        envelope = self.server.read()
        try:            
            if envelope.command == request_block.command:
                start_block, end_block = request_block.parse(envelope.stream())
                self.sendBlockToRequestor(start_block)
                print(f"Start Block is {start_block} \n End Block is {end_block}")
            
            self.conn.close()
        except Exception as e:
            self.conn.close()
            print(f" Error while processing the client request \n {e}")

    def sendBlockToRequestor(self, start_block):
        blocksToSend = self.fetchBlocksFromBlockchain(start_block)

        try:
            self.sendBlock(blocksToSend)
            self.sendFinishedMessage()
        except Exception as e:
            print(f"Unable to send the blocks \n {e}")

    def fetchBlocksFromBlockchain(self, start_Block):
        fromBlocksOnwards = start_Block.hex()

        blocksToSend = []
        blockchain = BlockchainDB()
        blocks = blockchain.read()

        foundBlock = False 
        for block in blocks:
            if block['BlockHeader']['blockHash'] == fromBlocksOnwards:
                foundBlock = True
                continue
        
            if foundBlock:
                blocksToSend.append(block)
        
        return blocksToSend
    
    def sendBlock(self, blockstoSend):
        for block in blockstoSend:
            cblock = Block.to_obj(block)
            envelope = network_envelope(cblock.command, cblock.serialize())
            self.conn.sendall(envelope.serialize())
            print(f"Block Sent {cblock.Height}")

    def sendFinishedMessage(self):
        MessageFinish = finished_sending()
        envelope = network_envelope(MessageFinish.command, MessageFinish.serialize())
        self.conn.sendall(envelope.serialize())

    def start_download(self, port):
        lastBlock = BlockchainDB().lastBlock()

        #Gensis Block
        if not lastBlock:
            lastBlockHeader = "0000107e701d483984ecf652b2ef324589d61f425d8f9a77b12ecdfcf4a17ce4"
        #Last Block
        else:
            lastBlockHeader = lastBlock['BlockHeader']['blockHash']

        start_block = bytes.fromhex(lastBlockHeader)

        get_headers = request_block(start_block=start_block)
        self.connect = Node(self.host, port)
        self.socket = self.connect.connect(port)
        self.connect.send(get_headers)

        while True:    
            envelope = network_envelope.parse(self.stream)
            if envelope.command == b"Finished Sending":
                blockObj = finished_sending.parse(envelope.stream())
                print(f"All Blocks Received")
                self.socket.close()
                break


            if envelope.command == b'block':
                blockObj = Block.parse(envelope.stream())
                BlockHeaderObj = BlockHeader(blockObj.BlockHeader.version,
                            blockObj.BlockHeader.prevBlockHash, 
                            blockObj.BlockHeader.merkleRoot, 
                            blockObj.BlockHeader.timestamp,
                            blockObj.BlockHeader.bits,
                            blockObj.BlockHeader.nonce)



