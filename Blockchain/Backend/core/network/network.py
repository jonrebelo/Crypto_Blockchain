from Blockchain.Backend.util.util import int_to_little_endian, little_endian_to_int, hash256, encode_varint
from io import BytesIO

NETWORK_MAGIC = b'\xf9\xbe\xb4\xd9'
FINISHED_SENDING =b'\x0a\x11\x09\x07'

class network_envelope:
    """
    The `network_envelope` class is used to encapsulate network messages in a format that includes various metadata along with the message payload.

    Attributes:
    command: A byte string that represents the type of message being sent.
    payload: The actual data or message being sent.
    magic: A value that identifies the network on which the message is being sent.

    Methods:
    __init__(self, command, payload): Initializes an instance of the class with a `command` and a `payload`. 
        The `magic` attribute is set to the constant `NETWORK_MAGIC`.

    serialize(self): Converts the instance into a byte string that can be sent over the network. 
        The serialized format includes the `magic` value, the `command` (padded with zeroes to a length of 12 bytes), 
        the length of the `payload` as a 4-byte little-endian integer, a 4-byte checksum of the `payload`, and the `payload` itself.
    """
    def __init__(self, command, payload):
        self.command = command
        self.payload = payload
        self.magic = NETWORK_MAGIC

    @classmethod
    def parse(cls, s):
        """
    Class method to parse a byte stream into a `network_envelope` instance.

    The method reads the various parts of the byte stream in the order they are expected to appear based on the network protocol.
    These parts include the `magic` value, the `command`, the `payload_length`, the `checksum`, and the `payload`.

    If the `magic` value read from the stream does not match the expected `NETWORK_MAGIC` constant, a `RuntimeError` is raised.

    The `command` is read as a 12-byte string and any trailing zero bytes are stripped.

    The `payload_length` is read as a 4-byte little-endian integer.

    The `checksum` is read as a 4-byte string.

    The `payload` is read as a byte string of length `payload_length`.

    A `calculated_checksum` is computed from the `payload` and if it does not match the `checksum` read from the stream, an `IOError` is raised.

    If all parts are successfully read and the checksums match, a new `network_envelope` instance is created with the `command` and `payload` and returned.
    """
        magic = s.read(4)

        if magic != NETWORK_MAGIC:
            raise RuntimeError(f"Magic is not right {magic.hex()} vs {NETWORK_MAGIC.hex()}")
        
        command = s.read(12)
        command = command.strip(b'\x00')
        payloadLen = little_endian_to_int(s.read(4))
        checksum = s.read(4)
        payload = s.read(payloadLen)
        calculatedChecksum = hash256(payload)[:4]

        if calculatedChecksum != checksum:
            raise IOError("Checksum does not match")
        
        return cls(command, payload)

    def serialize(self):
        result = self.magic
        result += self.command + b'\x00' * (12 - len(self.command))
        result += int_to_little_endian(len(self.payload), 4)
        result += hash256(self.payload)[:4]
        result += self.payload
        return result 
    
    def stream(self):
        return BytesIO(self.payload)
    
class request_block:
    """
    The `request_blocks` class is used to handle requests for blocks in a blockchain network. 

    Attributes:
    command: A byte string that identifies the type of request this class represents in the network protocol.

    Methods:
    __init__(self, start_block=None, end_block=None): Initializes an instance of the class with a `start_block` and an `end_block`. 
        If `start_block` is not provided, it raises a `RuntimeError`. If `end_block` is not provided, it defaults to a 32-byte string of zeroes.

    parse(cls, stream): Class method that reads 32 bytes each from a given stream to get the `start_block` and `end_block`. It returns these as a tuple.

    serialize(self): Concatenates the `start_block` and `end_block` attributes and returns the result. This is used when sending a block request over the network.
    """
    command = b'requestBlock'

    def __init__(self, start_block = None, end_block = None) -> None:
        if start_block is None:
            raise RuntimeError("Starting Block cannot be None")
        else:
            self.start_block = start_block
        
        if end_block is None:
            self.end_block = b'\x00' * 32
        else: 
            self.end_block = end_block

    @classmethod
    def parse(cls, stream):
        start_block = stream.read(32)
        end_block = stream.read(32)
        return start_block, end_block

    def serialize(self):
        result = self.start_block
        result += self.end_block
        return result 
    
class finished_sending:
    """
    The `finished_sending` class represents a network message indicating that a sender has finished sending data.

    Attributes:
    command: A byte string that represents the type of message being sent.

    Methods:
    parse(cls, s): Class method to parse a byte stream into a `finished_sending` instance.
        The method reads the first 4 bytes of the stream and checks if they match the `FINISHED_SENDING` constant.
        If they match, it returns the string "Finished Sending".

    serialize(self): Converts the instance into a byte string that can be sent over the network. 
        The serialized format is simply the `FINISHED_SENDING` constant.
    """

    command = b'Finished Sending'

    @classmethod
    def parse(cls, s):
        magic = s.read(4)

        if magic == FINISHED_SENDING:
            return "Finished Sending"

    def serialize(self):
        result = FINISHED_SENDING
        return result

