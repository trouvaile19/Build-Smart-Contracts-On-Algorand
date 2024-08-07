from algopy import ARC4Contract, Account, Asset, Global, LocalState, String, Txn, gtxn, UInt64, arc4, itxn
from algopy.arc4 import abimethod


class Auction(ARC4Contract):
    # Auction
    # Start Price
    # Bid - Bid Price > Start Price 
    # Bid - Bid Price > Previous Price
    # Bidder != Previous Bidder
    # Start Time - End Time
    # If Auction End -> End Time -> 0
    # Amount -> Claim

    def __init__(self) -> None:
        self.start_time = UInt64(0) # auction start
        self.end_time = UInt64(0) # auction end
        self.asa_amount = UInt64(0) # 1000 - bid price > asa amount 
        self.asa = Asset() # Tokens (ex: VBI Tokens) -> call in once
        self.previous_bidder = Account()
        self.claimble_amount = LocalState(UInt64, key = "claim", description = "the claimble amount") # key - value

    # Opt Asset (? Tokens)
    @arc4.abimethod # asset VBI tokens 
    def opt_into_asset(self, asset: Asset) -> None: # đưa sản phầm đấu giá vào
        assert Txn.sender == Global.creator_address, "Only creator has  access"
        assert self.asa == 0, "ASA already exists"
        self.asa = asset
        itxn.AssetTransfer (
            xfer_asset = asset,
            asset_receiver = Global.current_application_address

        ).submit()

    # Start Auction 
    def start_auction(self, starting_price: UInt64, duration: UInt64, axfer: gtxn.AssetTransferTransaction) -> None: # bắt đầu đáu giá
        assert Txn.sender == Global.creator_address, "Auction must be started by creator"
        assert self.end_time == 0, "Auction ended"
        assert axfer.asset_receiver == Global.current_application_address, "Axfer must be to this application"

        self.asa_amount = starting_price 
        self.end_time = duration + Global.latest_timestamp
        # global -> Unix Time -> 012312419 + 10001
        self.previous_bidder = Txn.sender
    
    # Bids
    @arc4.abimethod
    def bid(self, pay: gtxn.PaymentTransaction) -> None: # đấu giá
        # check the auction ended or not
        assert Global.latest_timestamp <= self.end_time, "auction ended"

        #verufy payment
        assert Txn.sender == self.previous_bidder, ""
        assert Txn.sender == pay.sender, "verify again"
        assert pay.amount > self.asa_amount

        # set data on global state
        self.asa_amount = pay.amount
        self.previous_bidder = Txn.sender

        # update claimable amount 
        self.claimble_amount[Txn.sender] = pay.amount
        # key (wallet address) -> value (amount)

    # Claim Bids
    @arc4.abimethod
    def claim_asset(self, asset: Asset) -> None: # chuyển sản phẩn đấu giá cho người thắng cuộc
        assert Txn.sender == Global.creator_address, "Auction must be started by creator"
        assert Global.latest_timestamp > self.end_time, "auction has not ended yet"

        itxn.AssetTransfer( # transfer of asset ownership inner transaction
            xfer_asset = asset, # is a parameter representing this asset you wan to tranfer
            asset_receiver = self.previous_bidder, # receiver who is a previous bidder
            asset_close_to = self.previous_bidder,
            asset_amount = self.asa_amount, # storage the highest amount bidded
        ).submit()
    
    @arc4.abimethod
    def claim_bids(self) -> None: 
        amount = self.claimble_amount[Txn.sender] # lấy được tokens mà pre-bidder có
        if Txn.sender == self.previous_bidder:
            amount = amount - self.asa_amount # -tokens after winning bid

        itxn.Payment(
            amount = amount,
            receiver = Txn.sender
        ).submit()
    
    # Delete Application
    @arc4.abimethod
    def delete_application(self) -> None:
        itxn.Payment(
            close_remainder_to = Global.creator_address,
            receiver = Global.creator_address
        ).submit()
# close Payment - close the right access of creator to this application
# remove the smart contract application from the blockchain and ensures 
# that all remaining Algos in the application's account are safely transferred back to the application creator
