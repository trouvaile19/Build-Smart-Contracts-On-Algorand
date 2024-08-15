from algopy import ARC4Contract, Account, Asset, Global, String, Txn, UInt64, gtxn, itxn, arc4, op, subroutine
from algopy.arc4 import abimethod

FOR_SALE_BOX_KEY_LENGTH = 48
FOR_SALE_BOX_VALUE_LENGTH = 64
# Create box -> 0.0025 algos (fee)
# byte per box -> 0.0004 algos (fee)
FOR_SALE_BOX_SIZE = FOR_SALE_BOX_KEY_LENGTH + FOR_SALE_BOX_VALUE_LENGTH
FOR_SALE_BOX_MBR = 2_500 + FOR_SALE_BOX_SIZE * 400
# d, "MBR":  Minimum Balance Requirement
class AdvMarketplace(ARC4Contract):
    # opt-into-access (co nhieu access hon)
    # allow_access
    # deposit
    # first_deposit
    # withdraw
    # buy
    @subroutine
    def quantity_price(
        self, quantity: UInt64, price: UInt64, asset_decimals: UInt64
    ) -> UInt64:
        amount_not_scaled_high, amount_not_scaled_low = op.mulw(price, quantity)
        scaling_factor_high, scaling_factor_low = op.expw(10, asset_decimals)
        _quotient_high, amount_to_be_paid, _remainder_high, _remainder_low = op.divmodw(
            amount_not_scaled_high,
            amount_not_scaled_low,
            scaling_factor_high,
            scaling_factor_low,
        )
        assert not _quotient_high

        return amount_to_be_paid

    @abimethod()
    def allow_access(self, name: String, mbr_pay: gtxn.PaymentTransaction, asset: Asset) -> None:
        # assert not Global.current_application_address.is_opted_in(asset), "asset already exists"
        
        # assert mbr_pay.receiver == Global.current_application_address
        # assert mbr_pay.amount == Global.asset_opt_in_min_balance

        itxn.AssetTransfer(
            xfer_asset = asset,
            asset_receiver = Global.current_application_address,
            asset_amount = 0,
            fee = 0 # -> cover fee -> application
        ).submit()

        # Keys -> Values
        # asset_id (unitary_price) -> amounts -> Box (storage) -> Bytes
    @abimethod()
    def first_deposit(self, xfer: gtxn.AssetTransferTransaction, nonce: arc4.UInt64, unitary_price: arc4.UInt64, mbr_pay: gtxn.PaymentTransaction) -> None:
        assert mbr_pay.sender == Txn.sender
        assert mbr_pay.receiver == Global.current_application_address
        assert mbr_pay.amount == FOR_SALE_BOX_MBR
        # create = 0.0025 algo
        # per byte = 0.0004 algos

        # address + asset_id + nonce                                    arc4.Uint64 to calculate
        box_key = Txn.sender.bytes + op.itob(xfer.xfer_asset.id) + nonce.bytes
        # box -> [....]              # -> convert to bytes
        _length, exists = op.Box.length(box_key)
        assert not exists

        assert xfer.sender == Txn.sender
        assert xfer.asset_receiver == Global.current_application_address
        assert xfer.asset_amount > 0
        # deposited, selling price, bidder, bid quantity, bid price
        # address (32) + UInt (8) + UInt (8) -> amount (8) + unitary_price (8)
        # 48 -> 16 = 64
        assert op.Box.create(box_key, FOR_SALE_BOX_VALUE_LENGTH) # assert tạo box -> 64 bit, if valid then storage
        op.Box.replace(box_key, 0, op.itob(xfer.asset_amount) + unitary_price.bytes)
        # a: address; b: offset (position); c: value (bytes)
        # ~ hash -> key -> value
        
        # global state
    @abimethod
    def deposit(self, xfer: gtxn.AssetTransferTransaction, nonce: arc4.UInt64) -> None:
        box_key = Txn.sender.bytes + op.itob(xfer.xfer_asset.id) + nonce.bytes
        _length, exists = op.Box.length(box_key)
        assert exists

        assert xfer.sender == Txn.sender
        assert xfer.asset_receiver == Global.current_application_address
        assert xfer.asset_amount > 0

        # 100 -> tokens
        # 50 -> tokens (overiding) therefore need to plus current_amount
        current_deposited = op.btoi(op.Box.extract(box_key, 0, 8)) # storage int (by convert byte into int)
        op.Box.replace(box_key, 0, op.itob(current_deposited + xfer.asset_amount)) # convert int into byte and storage

    @abimethod
    def set_price(self, asset : UInt64, nonce: arc4.UInt64, unitary_price: arc4.UInt64) -> None:
        box_key = Txn.sender.bytes + op.itob(asset) + nonce.bytes

        op.Box.replace(box_key, 8, unitary_price.bytes)
        # int 8 + 8 =16; bytes: 8 + 8 = 88

    @abimethod
    def withdraw(self, asset: Asset, nonce: arc4.UInt64) -> None:
        box_key = Txn.sender.bytes + op.itob(asset.id) + nonce.bytes
        
        current_deposit = op.btoi(op.Box.extract(box_key, 0, 8))
        current_bidder = Account(op.Box.extract(box_key, 16, 32))
        if current_bidder != Global.zero_address:
            current_bid_deposit = self.quantity_price(
                op.btoi(op.Box.extract(box_key, 48, 8)),
                op.btoi(op.Box.extract(box_key, 56, 8)),
                asset.decimals,   
            )
            itxn.Payment(
                receiver = current_bidder,
                amount = current_bid_deposit,
                fee = 0
            ).submit()

        _delete = op.Box.delete(box_key)

        itxn.Payment(
            receiver = Txn.sender,
            amount = FOR_SALE_BOX_MBR,
            fee = 0
        ).submit()

        itxn.AssetTransfer(
            xfer_asset = asset,
            asset_receiver = Txn.sender,
            asset_amount = current_deposit,
            fee = 0,
        ).submit()

    # retrancy attacks
    @abimethod
    def buy(self, owner: arc4.Address, asset: Asset, nonce: arc4.UInt64, buy_pay: gtxn.PaymentTransaction, quantity: UInt64) -> None:
        box_key =  owner.bytes + op.itob(asset.id) + nonce.bytes
        current_unitary_price = op.btoi(op.Box.extract(box_key, 8, 8))
       
        amount_to_be_paid = self.quantity_price(
            quantity, current_unitary_price, asset.decimals
        )
        
        assert buy_pay.sender == Txn.sender
        assert buy_pay.receiver.bytes == owner.bytes
        assert buy_pay.amount == amount_to_be_paid

        # 16 decimals
        # 6 decimals = 1000
        # 2 decimal = 2000
        # 1000 2000

        # 1000 tokens -> transfer 100

        current_deposited = op.btoi(op.Box.extract(box_key, 0, 8))
        op.Box.replace(box_key, 0, op.itob(current_deposited - quantity))

        itxn.AssetTransfer(
            xfer_asset = asset,
            asset_receiver = Txn.sender,
            asset_amount = quantity,
            fee = 0
        ).submit()  
        # newtokens = currentTokens - tokensTransfer

    # start to bid
    @abimethod
    def bid(self, bid_pay: gtxn.PaymentTransaction, asset: Asset, nonce: arc4.UInt64, owner: arc4.Address, unitary_price: arc4.UInt64, quantity: arc4.UInt64) -> None:
                                                                                    #unitary_price: số tiền to bid
        assert Txn.sender.is_opted_in(asset)                            
        box_key = owner.bytes + op.itob(asset.id) + nonce.bytes
        
        # 0 -> 16 ( amount, unitary_price ) (storaged)
        current_bidder = Account(op.Box.extract(box_key, 16, 32)) # address -> 32 bytes
        if current_bidder != Global.zero_address: # if current_bidder hasn't address yet
            current_bid_quantity = op.btoi(op.Box.extract(box_key, 48, 8)) # start at byte: 48 and the expand to 8 bytes
            current_bid_unitary_price = op.btoi(op.Box.extract(box_key, 56, 8))
            assert unitary_price > current_bid_unitary_price
            # 1000 -> previous bidder
            current_bid_amount = self.quantity_price(
                current_bid_quantity, current_bid_unitary_price, asset.decimals
            )
        
            itxn.Payment(
                receiver = current_bidder,
                amount = current_bid_amount,
                fee = 0
            ).submit()
        amount_to_be_bid = self.quantity_price(
            quantity.native, 
            unitary_price.native,
            asset.decimals 
        )
        assert bid_pay.sender == Txn.sender
        assert bid_pay.receiver == Global.current_application_address
        assert bid_pay.amount == amount_to_be_bid

        op.Box.replace(box_key, 16, Txn.sender.bytes + quantity.bytes + unitary_price.bytes)

    @abimethod # Terminated
    def accept_bid(self, asset: Asset, nonce: arc4.UInt64) -> None:
        box_key = Txn.sender.bytes + op.itob(asset.id) + nonce.bytes

        best_bidder = Account(op.Box.extract(box_key, 16, 32)) # address -> 32 bytes
        assert best_bidder != Global.zero_address

        best_bid_quantity = op.btoi(op.Box.extract(box_key, 48, 8))
        best_bid_unitary_price = op.btoi(op.Box.extract(box_key, 56, 8))        
        current_deposited = op.btoi(op.Box.extract(box_key, 48, 8))
        current_unitary_price = op.btoi(op.Box.extract(box_key, 8, 8))

        assert current_unitary_price > best_bid_unitary_price
            
        # min_quantity
        min_quantity = current_deposited if current_deposited < best_bid_quantity else best_bid_quantity
        # 10_000 -> quantity -> 9000
        best_bid_amount = self.quantity_price(
            min_quantity, best_bid_unitary_price, asset.decimals
        )

        itxn.Payment(
            receiver = Txn.sender,
            amount = best_bid_amount,
            fee = 0
        ).submit()

        op.Box.replace(box_key, 0, op.itob(current_deposited - min_quantity )) # 9_000 - 9_000
        op.Box.replace(box_key, 48, op.itob(best_bid_quantity - min_quantity)) # 10_000 - 9000 = 100
