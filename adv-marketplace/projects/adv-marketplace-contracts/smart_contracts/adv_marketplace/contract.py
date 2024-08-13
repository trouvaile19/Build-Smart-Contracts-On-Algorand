from algopy import ARC4Contract, Account, Asset, Global, String, Txn, UInt64, gtxn, itxn, arc4, op, subroutine
from algopy.arc4 import abimethod

BOX_LENGTH_FOR_SALE = 64
MINIMUM_FEE_FOR_SALE = 2_500 + 400 + BOX_LENGTH_FOR_SALE

class AdvMarketplace(ARC4Contract):
    # opt-into-access (co nhieu access hon)
    # allow_access
    # deposit
    # first_deposit
    # withdraw
    # buy
    

    @abimethod()
    def allow_access(self, name: String, pay: gtxn.PaymentTransaction, asset: Asset) -> None:
        assert not Global.current_application_address.is_opted_in(asset)
        
        assert pay.receiver == Global.current_application_address
        assert pay.amount == Global.asset_opt_in_min_balance

        itxn.AssetTransfer(
            xfer_asset = asset,
            asset_receiver = Global.current_application_address,
            asset_amount = 0,
            fee = 0 # -> cover fee -> application
        ).submit()

        # Keys -> Values
        # asset_id (unitary_price) -> amounts -> Box (storage) -> Bytes
    @abimethod()
    def first_deposit(self, xfer: gtxn.AssetTransferTransaction, nonce: arc4.UInt64, unitary_price: arc4.UInt64, pay: gtxn.PaymentTransaction) -> None:
        assert pay.sender == Txn.sender
        assert pay.receiver == Global.current_application_address
        assert pay.amount == MINIMUM_FEE_FOR_SALE
        # create = 0.0025
        # per byte = 0.0004

        # address + asset_id + nonce                                    arc4.Uint64 to calculate
        box_key = Txn.sender.bytes + op.itob(xfer.xfer_asset.id) + nonce.bytes
        # box -> [....]              # -> convert to bytes
        _length, exists = op.Box.length(box_key)
        assert not exists

        assert xfer.sender == Txn.sender
        assert xfer.receiver == Global.current_application_address
        assert xfer.amount > 0

        # address (32) + UInt (8) + UInt (8) -> amount (8) + unitary_price (8)
        # 48 -> 16 = 64
        assert op.Box.create(box_key, BOX_LENGTH_FOR_SALE) # assert tạo box -> 64 bit, if valid then storage
        op.Box.replace(box_key, 0, op.itob(xfer.asset_amount) + unitary_price.bytes)
        # a: address; b: offset (position); c: value
        # hash -> key -> value
        
        # global state
    @abimethod
    def deposit(self, xfer: gtxn.AssetTransferTransaction, nonce: arc4.UInt64) -> None:
        box_key = Txn.sender.bytes + op.itob(xfer.xfer_asset.id) + nonce.bytes
        _length, exists = op.Box.length(box_key)
        assert exists

        assert xfer.sender == Txn.sender
        assert xfer.receiver == Global.current_application_address
        assert xfer.amount > 0

        # 100 -> tokens
        # 50 -> tokens (overiding) therefore need to plus current_amount
        current_amount = op.btoi(op.Box.extract(box_key, 0, 8)) # storage int (by convert byte into int)
        op.Box.replace(box_key, 0, op.itob(xfer.asset_amount + current_amount)) # convert int into byte and storage

    @abimethod
    def set_price(self, asset_id : UInt64, nonce: arc4.UInt64, unitary_price: arc4.UInt64) -> None:
        box_key = Txn.sender.bytes + op.itob(asset_id) + nonce.bytes

        op.Box.replace(box_key, 8, unitary_price.bytes)
        # int 8 + 8 =16; bytes: 8 + 8 = 88

    # retrancy attacks
    @abimethod
    def buy(self, buyer: arc4.Address, asset: Asset, nonce: arc4.UInt64, buyer_txn: gtxn.PaymentTransaction, quantity: UInt64) -> None:
        box_key = Txn.sender.bytes + op.itob(asset.id) + nonce.bytes
        current_unitary_price = op.btoi(op.Box.extract(box_key, 8, 8))
       
        amount_to_paid = self._quantity_price(
            quantity, current_unitary_price, asset.decimals
        )
        
        assert buyer_txn.sender == Txn.sender
        assert buyer_txn.receiver == buyer
        assert buyer_txn.amount == amount_to_paid

        # 16 decimals
        # 6 decimals = 1000
        # 2 decimal = 2000
        # 1000 2000

        # 1000 tokens -> transfer 100

        current_amount = op.btoi(op.Box.extract(box_key, 0, 8))
        op.Box.replace(box_key, 0, op.itob(current_amount - quantity))

        itxn.AssetTransfer(
            xfer_asset = asset,
            asset_receiver = Txn.sender,
            asset_amount = quantity,
            fee = 0
        ).submit()  
        # newtokens = currentTokens - tokensTransfer

    @subroutine
    def _quantity_price(self, quantity: UInt64, price: UInt64, asset_decimals: UInt64) -> UInt64:
        amount_scaled_high, amount_scaled_low = op.mulw(price, quantity) # chia
        scalling_high, scalling_low = op.expw(10, asset_decimals) # 10^8 => 100_000_000
        _a,amount_to_paid,_remainder_high,_remainder_low = op.divmodw(
            amount_scaled_high,
            amount_scaled_low,
            scalling_high,
            scalling_low
        )
        assert not _a

        return amount_to_paid
    # start to bid
    @abimethod
    def bid(self, pay: gtxn.PaymentTransaction, asset: Asset, nonce: arc4.UInt64, owner: arc4.Address, unitary_price: UInt64, quantity: arc4.UInt64) -> None:
        assert Txn.sender.is_opted_in(asset)                            #unitary_price: số tiền to bid
        box_key = owner.bytes + op.itob(asset.id) + nonce.bytes
        
        # 0 -> 16 ( amount, unitary_price ) (storaged)
        current_bidder = Account(op.Box.extract(box_key, 16, 32)) # address -> 32 bytes
        if current_bidder != Global.zero_address: # if current_bidder hasn't address yet
            current_bid_quantity = op.btoi(op.Box.extract(box_key, 48, 8)) # start at byte: 48 and the expand to 8 bytes
            current_bid_unitary_price = op.btoi(op.Box.extract(box_key, 56, 8))
            assert unitary_price > current_bid_unitary_price
            # 1000 -> previous bidder
            current_bid_amount = self._quantity_price(
                current_bid_quantity, current_bid_unitary_price, asset.decimals
            )
        
        itxn.Payment(
            receiver = current_bidder,
            amount = current_bid_amount,
            fee = 0
        ).submit()
        amount_to_paid = self._quantity_price(
            quantity.native, 
            unitary_price,
            asset.decimals 
        )
        assert pay.sender == Txn.sender
        assert pay.receiver == Global.current_application_address
        assert pay.amount == amount_to_paid

        op.Box.replace(box_key, 16, Txn.sender.bytes + quantity.bytes + unitary_price.bytes)

    @abimethod # Terminated
    def accept_bid(self, asset: Asset, nonce: arc4.UInt64) -> None:
        box_key = Txn.sender.bytes + op.itob(asset.id) + nonce.bytes

        winner = Account(op.Box.extract(box_key, 16, 32)) # address -> 32 bytes
            
        highest_bid_quantity = op.btoi(op.Box.extract(box_key, 48, 8))
        highest_bid_unitary_price = op.btoi(op.Box.extract(box_key, 56, 8))
            
        current_quantity = op.Box.extract(box_key, 48, 8)
        current_unitary_price = op.Box.extract(box_key, 8, 8)

        assert current_unitary_price > highest_bid_unitary_price
            
        # min_quantity
        min_quantity = current_quantity if current_quantity < highest_bid_quantity else highest_bid_quantity
        # 10_000 -> quantity -> 9000
        highest_bid_amount = self._quantity_price(
            min_quantity, highest_bid_unitary_price, asset.decimals
        )

        op.Box.replace(box_key, 0, op.itob(current_quantity - min_quantity )) # 9_000 - 9_000
        op.Box.replace(box_key, 48, op.itob(highest_bid_quantity - min_quantity)) # 10_000 - 9000 = 100

        itxn.Payment(
            receiver = Txn.sender,
            amount = highest_bid_amount,
            free = 0
        ).submit()
