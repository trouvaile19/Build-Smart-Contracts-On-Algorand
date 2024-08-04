from algopy import ARC4Contract, Account, Asset, Global, String, Txn, UInt64, arc4, subroutine
from algopy.arc4 import abimethod

# AVM - Algorand Virtual Machine
# change - Consensus (node -> node -> cost to change data)
# Back-end -> Cloud EC2 AWS -> (bytecode) -> On-chain 
# onchain
# offchain ->

class Ama(ARC4Contract):
    num_tmp: UInt64 # unsigned integer
    num2: arc4.UInt64
    text: String
    asset: Asset # class(struct) lien quan den tocken
    account: Account # dai dien cho dia chi vi

    def __init__(self) -> None:
        self.num_tmp = UInt64(0)

    @subroutine
    def test_num1(self) -> UInt64:
        assert Txn.receiver == Global.current_application_address       
        return self.num_tmp + 10
    
    @arc4.abimethod() # goi cac function on-chain
    def hello(self) -> UInt64:
        return self.test_num1()


# 'algokit project run build' -> create folder artifacts
# file.teal: functions
# tests -> ama_test.py
