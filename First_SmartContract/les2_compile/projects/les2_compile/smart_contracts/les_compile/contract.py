# Create, update a Smart Contract
from algopy import ARC4Contract, arc4, UInt64, Asset, Global, Txn, gtxn, itxn
from algopy.arc4 import abimethod
# global
# Txn - transaction
# gtxn - global transaction 
# ilxn - interface transaction

class LesCompile(ARC4Contract):
    # local storage
    asset_id: UInt64  
    price: UInt64
    
    @arc4.abimethod(create="require", allow_actions = ["NoOp"])
    def create_application(self, asset_id: Asset, price: UInt64) -> None: #no return
        self.asset_id = asset_id.id
        self.price = price

    @arc4.abimethod
    def update_price(self, new_price: UInt64) -> UInt64:
        # Check that txn sender (Txn.sender) must match the creator txn (creator_address)   
        assert Txn.sender == Global.creator_address #'Global' variable
        # update new price
        self.price = new_price
        return new_price
    
    @arc4.abimethod
    # buyer_txn to storage an address & gtxn on BC
    def buy(self, buyer_txn: gtxn.PaymentTransaction, quanity: UInt64) -> None: 
            assert self.price != 0      #check valid money
            assert Txn.sender == buyer_txn.sender    #check valid sender
            assert buyer_txn.amount == self.price * quanity // 10 *20  #chẹc
            
            itxn.AssetTransfer(
                 xfer_asset=self.asset_id,   # retrieve asset_id
                 asset_receiver= Txn.sender,     # send to buyer (asset_receiver 
                 asset_amount=quanity,
            ).submit()

# The functions within the contract will always be passed 'self' (ARC4Contract).
# @arc4.abimethod to definite SC methods for Algorand (), save method on SC.
# Check that txn sender (Txn.sender) must match the creator txn (creator_address),
# so that we can avoid being adjusting contract by any people who know asset_id.
# gtxn retrieves data from the global transaction to synchronize with all nodes on BC
