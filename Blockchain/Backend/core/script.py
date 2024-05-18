from Blockchain.Backend.util.util import int_to_little_endian, encode_varint
from Blockchain.Backend.core.EllepticCurve.op import OP_CODE_FUNCTION
class Script:
    def __init__(self, cmds = None):
        if cmds is None:
            self.cmds = []
        else:
            self.cmds = cmds

    def __add__(self, other):
        #override addition operation to add commands when script is added
        return Script(self.cmds + other.cmds)

    
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

        #get the length of the entire thing        
        total = len(result)

        #encode_varint the total length
        return encode_varint(total) + result

    def evaluate(self, z):

        """This function evaluates a list of commands (self.cmds) using a stack-based approach. 
    It iterates over the commands, and for each command, it performs an operation based on its type.
    Parameters:
    z: A hash used in the op_checksig operation.
    Returns:
    None. However, it prints an error message and returns False if an operation fails."""

    def evaluate(self, z):
        # Copy the list of commands
        cmds = self.cmds[:]
        # Initialize an empty stack
        stack = []

        # Iterate over the commands while there are commands left
        while len(cmds) > 0:
            # Pop the first command from the list
            cmd = cmds.pop(0)
            # If the command is an integer, it's an operation code
            if type(cmd) == int:
                # Get the corresponding operation function from the OP_CODE_FUNCTION dictionary
                operation = OP_CODE_FUNCTION[cmd]
                # If the operation code is 172 (op_checksig), perform the operation with the stack and z as arguments
                if cmd == 172:
                    if not operation(stack, z):
                        print(f"Error in Signature Verification")
                        return False
                    # For other operation codes, perform the operation with the stack as the argument
                elif not operation(stack):
                    print(f"Error in Signature Verification")
                    return False
                # If the command is not an integer, it's a value to be pushed onto the stack
            else:
                stack.append(cmd)
        return True

    @classmethod
    def p2pkh_script(cls, h160):
        """
        Takes hash160 and returns the p2pkh Script_Pubkey.
        """
        return Script([0x76, 0xa9, h160, 0x88, 0xac])