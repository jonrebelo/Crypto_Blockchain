from Blockchain.Backend.util.util import hash160
from Blockchain.Backend.core.EllepticCurve.EllepticCurve import Sha256Point, Signature


def op_dup(stack):
    """
    Duplicates the top item on the stack.
    If the stack is empty, returns False.
    """
    if len(stack) < 1:
        return False
    stack.append(stack[-1])
    return True


def op_hash160(stack):
    """
    Removes the top item from the stack, hashes it with SHA-256, then RIPEMD-160,
    and pushes the result back onto the stack.
    If the stack is empty, returns False.
    """
    if len(stack) < 1:
        return False
    element = stack.pop()
    h160 = hash160(element)
    stack.append(h160)
    return True


def op_equal(stack):
    """
    Removes the top two items from the stack, compares them and pushes the result (1 if equal, 0 otherwise) onto the stack.
    If there are fewer than two items on the stack, returns False.
    """
    if len(stack) < 2:
        return False

    element1 = stack.pop()
    element2 = stack.pop()

    if element1 == element2:
        stack.append(1)
    else:
        stack.append(0)

    return True


def op_verify(stack):
    """
    Removes the top item from the stack and checks if it is non-zero.
    If it is zero or if the stack is empty, returns False.
    """
    if len(stack) < 1:
        False
    element = stack.pop()

    if element == 0:
        return False

    return True


def op_equalverify(stack):
    """
    Performs the op_equal operation and then op_verify on the result.
    """
    return op_equal(stack) and op_verify(stack)


def op_checksig(stack, z):
    """
    Checks the signature of the top item of the stack against the second item on the stack (which should be a public key),
    using the provided hash 'z'. If the signature is valid, pushes 1 onto the stack, otherwise pushes 0.
    If there are fewer than two items on the stack, returns False.
    """
    if len(stack) < 1:
        return False

    sec_pubkey = stack.pop()
    der_signature = stack.pop()[:-1]

    try:
        point = Sha256Point.parse(sec_pubkey)
        sig = Signature.parse(der_signature)
    except Exception as e:
        return False

    if point.verify(z, sig):
        stack.append(1)
        return True
    else:
        stack.append(0)
        return False


OP_CODE_FUNCTION = {118: op_dup, 136: op_equalverify, 169: op_hash160, 172: op_checksig}