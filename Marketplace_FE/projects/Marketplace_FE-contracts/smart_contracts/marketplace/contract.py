from algopy import ARC4Contract, Asset, Global, String, Txn, UInt64, gtxn, itxn
from algopy.arc4 import abimethod

class Marketplace(ARC4Contract):
    # Sell asset
    asset_id: UInt64
    # decimals -> 1 ETH 18 decimals -> Algorands -> USDT -> 8 decimals
    # 16 decimals -> USDT 8 decimals
    unitary_price: UInt64

    @abimethod(allow_actions=["NoOp"], create="require")
    def create_application(self, asset_id: Asset, unitary_price: UInt64) -> None:  # -> Application Id
        self.asset_id = asset_id.id
        self.unitary_price = unitary_price

    @abimethod
    def opt_in_to_asset(self, pay: gtxn.PaymentTransaction) -> None:
        assert Txn.sender == Global.creator_address
        assert not Global.current_application.address.is_opted_in(Asset(self.asset_id))

        assert pay.receiver == Global.current_application.address
        assert pay.amount == Global.min_balance + Global.asset_opt_in_min_balance

        itxn.AssetTransfer(
            xfer_asset=self.asset_id,
            asset_receiver=Global.current_application.address,
            asset_amount=0
        ).submit()
    @abimethod
    def set_price(self, unitary_price: UInt64) -> None:
        assert Txn.sender == Global.creator_address
        self.unitary_price = unitary_price

    @abimethod
    def buy(self, payer: gtxn.PaymentTransaction, quantity: UInt64) -> None:
        assert self.unitary_price != UInt64(0)
        assert payer.sender == Txn.sender
        assert payer.receiver == Global.current_application_address
        # 100 tokens * unitary_price (100 Algos)
        assert payer.amount == quantity * self.unitary_price

        itxn.AssetTransfer(
            xfer_asset=self.asset_id,
            asset_receiver=Txn.sender,
            asset_amount=quantity
        ).submit()

    @abimethod(allow_actions=["DeleteApplication"])
    def delete_application(self) -> None:
        assert Txn.sender == Global.creator_address

        itxn.AssetTransfer(
            xfer_asset=self.asset_id,
            asset_receiver=Global.creator_address,
            asset_amount=0,
            asset_close_to=Global.creator_address
        ).submit()

        itxn.Payment(
            receiver=Global.creator_address,
            amount=0,
            close_remainder_to=Global.creator_address
        ).submit()
