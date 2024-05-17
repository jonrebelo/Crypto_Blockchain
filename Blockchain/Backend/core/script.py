from Blockchain.Backend.util.util import int_to_little_endian, encode_varint

class Script:
    def __init__(self, cmds = None):
        if cmds is None:
            self.cmds = []
        else:
            self.cmds = cmds
    def serialize(self):
        #initialize what's being sent back
        result = b''
        #iterate through the commands
        for cmd in self.cmds:
            #if the command is an integer, turn it into a byte
            if type(cmd) == int:
                #convert integer to little endian
                result += int_to_little_endian(cmd, 1)
            else:
                #otherwise this is an element
                #get length in bytes
                length = len(cmd)
                #if the length is less than 75, it's an element
                if length < 75:
                    result += int_to_little_endian(length, 1)
                elif length > 75 and length <0x100:
                    #if the length is greater than 75, but less than 0x100, it's a 1 byte element
                    result += int_to_little_endian(76, 1)
                    result += int_to_little_endian(length, 1)
                elif length >= 0x100 and length < 520:
                    #if the length is greater than 0x100, but less than 520, it's a 2 byte element
                    result += int_to_little_endian(77, 1)
                    result += int_to_little_endian(length, 2)
                else:
                    raise ValueError("too long an cmd")
                
                result += cmd

        #get the length of the wntire thing        
        total = len(result)
        
        #encode_varint the total length
        return encode_varint(total) + result

    @classmethod
    def p2pkh_script(cls, h160):
        """
        Takes hash160 and returns the p2pkh Script_Pubkey.
        """
        return Script([0x76, 0xa9, h160, 0x88, 0xac])