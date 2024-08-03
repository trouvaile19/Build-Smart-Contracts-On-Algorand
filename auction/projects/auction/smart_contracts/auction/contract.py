from algopy import ARC4Contract, Account, Asset, LocalState, String, UInt64, gtxn, itxn
from algopy.arc4 import abimethod



class Auction(ARC4Contract):
    def __init__(self) -> None:
        # set time for auction
        self.auction_start = UInt64(0) 
        self.auction_end = UInt64(0)
        self.asa_amount = UInt64(0)
        self.asa = Asset() # ASA - Algorand Standard Assets
        # Asset is the token to pay auction 
        self.previous_bidder = Account() # the previous bidder
        self.claimble_amount = LocalState(UInt64, key = "claim ", description = "The claimble amount")
        #LocalState() Store the data in local first, then later modify and execute it on the BC


# key: point to find the location of localstate 
