from algopy import ARC4Contract, arc4, UInt64, Asset, Global, Txn, gtxn, itxn
from algopy.arc4 import abimethod
global
# Txn - transaction
# gtxn - global transaction 
# ilxn -

class LesCompile(ARC4Contract):
    # local storage
    asset_id: UInt64
    price: UInt64
    
    @arc4.abimethod(create="require", allow_actions = ["NoOp"])
    def create_application(self, asset_id: Asset, price: UInt64) -> None:
        self.asset_id = asset_id.id
        self.price = price

    @arc4.abimethod
    def update_price(self, new_price: UInt64) -> UInt64:
        assert Txn.sender == Global.creator_address

        self.price = new_price
        return new_price
    
    @arc4.abimethod
    def buy(self, buyer_txn: gtxn.PaymentTransaction, quality: UInt64) -> None:
            assert self.price != 0
            assert Txn.sender == buyer_txn.sender
            assert buyer_txn.amount == self.price * quality // 10 *20 
            
            itxn.AssetTransfer(
                 xfer_asset=self.asset_id,
                 asset_receiver= Txn.sender
                 asset_amount=quaility
            ).submit()
