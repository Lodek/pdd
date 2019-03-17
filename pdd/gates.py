from blocks import Gate

def AND(**kwargs):
    """Factory for Logic AND gate"""
    return Gate(op=Gate.AND, **kwargs)

def XOR(**kwargs):
    """Factory for Logic XOR gate"""
    return Gate(op=Gate.XOR, **kwargs)

def OR(**kwargs):
    """Factory for Logic OR gate"""
    return Gate(op=Gate.OR, **kwargs)
 
