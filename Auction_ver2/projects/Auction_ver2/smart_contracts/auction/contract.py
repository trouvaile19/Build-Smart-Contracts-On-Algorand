from algopy import ARC4Contract, Account, Asset, Global, LocalState, String, Txn, gtxn, UInt64, arc4, itxn
from algopy.arc4 import abimethod


class AuctionContract(ARC4Contract):
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
        self.previous_bid = UInt64(0)
        self.asa_amount = UInt64(0) # 1000 - bid price > asa amount 
        self.asa = Asset() # Tokens (ex: VBI Tokens) -> call in once
        self.claimable_amount = LocalState(UInt64, key = "claim", description = "the claimble amount") # key - value

    # Opt Asset (? Tokens)
    @arc4.abimethod # asset VBI tokens 
    def opt_into_asset(self, asset: Asset) -> None: # đưa sản phầm đấu giá vào
        assert Txn.sender == Global.creator_address, "Only creator can opt into ASA"
        assert self.asa.id == 0, "ASA already opted in"
        self.asa = asset # gắn asset vào để đấu giá
        itxn.AssetTransfer (
            xfer_asset = asset,
            asset_receiver = Global.current_application_address

        ).submit()

    # Start Auction 
    def start_auction(self, starting_price: UInt64, length: UInt64, axfer: gtxn.AssetTransferTransaction) -> None: # bắt đầu đáu giá
        assert Txn.sender == Global.creator_address, "Auction must be started by creator"
        # Ensure the auction hasn't already been started
        assert self.end_time == 0, "Auction already started"
        # Verify axfer
        assert axfer.asset_receiver == Global.current_application_address, "Axfer must be to this application"
        # Set global state
        self.asa_amount = axfer.asset_amount 
        self.end_time = length + Global.latest_timestamp
        # global -> Unix Time -> 012312419 + 10001
        self.previous_bid = starting_price
    
    # Bids
    @arc4.abimethod
    def bid(self, pay: gtxn.PaymentTransaction) -> None: # đấu giá
        # check the auction ended or not
        assert Global.latest_timestamp < self.end_time, "auction ended"

        # verify payment transaction
        assert pay.sender == Txn.sender, "Payment sender must match transaction sender"
        assert pay.amount > self.previous_bid, "Bid must be higher than previous bid" 

        # set global state
        self.previous_bid = pay.amount
        self.previous_bidder = pay.sender

        # update claimable amount 
        self.claimable_amount[Txn.sender] = pay.amount
        # key (wallet address) -> value (amount)

    # Claim Bids
    @arc4.abimethod
    def claim_bids(self) -> None: 
        amount = original_amount = self.claimable_amount[Txn.sender] # lấy được tokens mà pre-bidder có
        # subtract previous bid if sender is previous bideer
        if Txn.sender == self.previous_bidder:
            amount = amount - self.previous_bid # -tokens after winning bid

        itxn.Payment(
            amount = amount,
            receiver = Txn.sender,
        ).submit()

        self.claimable_amount[Txn.sender] = original_amount - amount
    
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
