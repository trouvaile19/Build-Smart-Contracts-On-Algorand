from algopy import ARC4Contract, String, UInt64, arc4
from algopy.arc4 import abimethod

class Counter (ARC4Contract):

    @abimethod()
    def add(self, a: UInt64, b: UInt64) -> UInt64:
        return a + b

    @abimethod()
    def mul(self, a: UInt64, b: UInt64) -> UInt64:
        assert a != 0, "a must be not equal 0"
        assert b != 0, "b must be not equal 0"
        return a * b

    @abimethod()
    def sub(self, a: UInt64, b: UInt64) -> UInt64:
        assert a > b, "b must be lower than a"
        return a - b

    @abimethod()
    def div(self, a: UInt64, b: UInt64) -> UInt64:
        assert a != 0, "a must be not equal 0"
        assert b != 0, "b must be not equal 0"
        return a // b
    
# 'algokit project run build' -> artifacts/
# counter_test.py -> test output -> 'algokit project run test'
