from algopy import ARC4Contract, Account, Asset, Global, LocalState, String, Txn, UInt64, gtxn, itxn, arc4
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
        self.previous_bid = UInt64
        self.claimble_amount = LocalState(UInt64, key = "claim ", description = "The claimble amount")
        #LocalState() Store the data in local first, then later modify and execute it on the BC

    @arc4.abimethod # storage data on-chain (be built by byte code and interact with smartcontract)
    def start_auction(self, end_at: UInt64, start_at: UInt64, starting_price: UInt64, exfer: gtxn.AssetTransferTransaction) -> None:
        # Txn.sender chính là người gọi start_auction
        # creator_address: creator of this contract
        # assert true => loi
        assert Txn.sender == Global.creator_address, "you're owner of auction" 
        assert Txn.sender == self.previous_bidder, "you're previous bidder"
        assert self.auction_end == 0, "auction done"
        assert Global.latest_timestamp >= end_at, "auction ended"
        assert start_at < end_at, "Start at must be lower end_at"
        assert exfer.asset_receiver != Global.current_application_address, "exfer must be transfer to this app"

        self.auction_end = Global.lastest_timestamp + end_at
        self.auction_start = Global.latest_timestamp + start_at
        self.previous_bid = starting_price


# key: point to the location of localstate 
# Sau khi compile contract.py('algokit compile .py 'path to contract.py') sẽ tạo ra 3 file output:
# Auction.arc32.json: giống file interface giúp tương tac front-end dễ dàng      
#      biết được các fiel trong contract là gì cũng như các dư liệu truyền vào
# Auction.approval.teal: các dữ liệu lưu trữ trên onchain
# Auction.clear.teal: 
