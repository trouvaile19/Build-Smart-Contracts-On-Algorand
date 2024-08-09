from collections.abc import Generator
import time

import pytest
from algopy_testing import AlgopyTestContext, algopy_testing_context

from smart_contracts.auction.contract import AuctionContract


@pytest.fixture()
def context() -> Generator[AlgopyTestContext, None, None]:
    with algopy_testing_context() as ctx:
        yield ctx
        ctx.reset()

    # no need to test __init__ function

def test_opt_into_asset(context: AlgopyTestContext) -> None:
    # AlgopyTestContext lấy dữ liệu ở trên môi trường BC
    # create an asset - fuzzing test ( test duoc nhieu case hon)
    asset = context.any_asset() # asset # VBI -0xlasklabc
    contract = AuctionContract() # init contract

    contract.opt_into_asset(asset)

    assert contract.asa.id == asset.id
    inner_txn = context.last_submitted_itxn.asset_transfer
    assert inner_txn.asset_receiver == context.default_application.address # 0xlasklabc
    assert inner_txn.xfer_asset == asset # vbi token
#_____________________________________________________________________
def test_start_auction(context: AlgopyTestContext) -> None:
    current_timestamp = context.any_uint64(1, 1000)
    duration_timestamp = context.any_uint64(1, 1000)
    # current + duration -> end-time
    starting_price = context.any_uint64()
    axfer_txn = context.any_asset_transfer_transaction(
        asset_amount = starting_price,
        asset_receiver = context.default_application.address
    )
    contract = AuctionContract()
    contract.asa_amount = starting_price
    context.patch_global_fields( # lấy ra được Key - value pairs for global fields
        latest_timestamp = current_timestamp
    )
    context.patch_txn_fields( # thông tin của 1 transaction sẽ cần những cái gì 
        sender = context.default_creator
    )
    contract.start_auction(
        starting_price = starting_price,
        length = duration_timestamp,
        axfer = axfer_txn
    )
    assert contract.end_time == current_timestamp + duration_timestamp
    assert contract.previous_bid == starting_price
    assert contract.asa_amount == starting_price                      
#_____________________________________________________________________
def test_bid(context: AlgopyTestContext) -> None: # test for bid function
    # account
    account = context.default_creator # -> nguoi goi contract 
    # account_end
    action_end = context.any_uint64(min_value=int(time.time() + 10000))
    # privious_bid to test
    privious_bid = context.any_uint64(1, 100) # co tinh sai trinh ta
    # amount 
    pay_amount = context.any_uint64(100, 1000)

    contract = AuctionContract()
    contract.end_time = action_end
    contract.previous_bid = privious_bid
    pay = context.any_payment_transaction(sender = account, amount = pay_amount )

    contract.bid(pay = pay)

    # assert 
    assert contract.previous_bid == pay_amount
    assert contract.previous_bidder == account
    assert contract.claimable_amount[account] == pay_amount
#________________________________________________________________________
def test_claim_bids(context: AlgopyTestContext) -> None:
    account = context.any_account()
    context.patch_txn_fields(sender = account)

    contract = AuctionContract()
    claimable_amount = context.any_uint64() # sum tokens of account
    
    # address -> amount
    contract.claimable_amount[account] = claimable_amount
    contract.previous_bidder = account
    previous_bid = context.any_uint64(max_value = int(claimable_amount))
    contract.previous_bid = previous_bid
    # Series -> Function
    contract.claim_bids()

    amount = claimable_amount - previous_bid # remaining amount after bid
    last_txn = context.last_submitted_itxn.payment

    assert last_txn.amount == amount 
    assert last_txn.receiver == account
    assert contract.claimable_amount[account] == claimable_amount - amount
