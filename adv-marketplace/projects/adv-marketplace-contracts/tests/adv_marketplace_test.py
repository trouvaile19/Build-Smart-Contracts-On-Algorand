from collections.abc import Generator
from algokit_utils.beta.algorand_client import AlgorandClient, PayParams
from algokit_utils.beta.composer import TransactionWithSigner
from algopy import Bytes, UInt64, arc4
import algopy
import pytest
from algopy_testing.arc4 import Address 
from algopy_testing import AlgopyTestContext, algopy_testing_context

from smart_contracts.adv_marketplace.contract import AdvMarketplace


@pytest.fixture()
def context() -> Generator[AlgopyTestContext, None, None]:
    with algopy_testing_context() as ctx:
        yield ctx
        ctx.reset()

def test_allow_asset(context: AlgopyTestContext) -> None:
    # mbbr_pay: minimun pay, asset
    sender = context.any_account(); 
    contract = AdvMarketplace();
    contract.__init__();
    asset = context.any_asset(creator = sender, decimals = UInt64(3), total = UInt64(10_000_000))

    app_address = context.default_application.address
    pay_txn = context.any_payment_transaction(sender = sender, receiver = app_address, amount = UInt64(0))
    # input payment Txn
    contract.allow_access(mbr_pay = pay_txn, asset = asset)
    itxn_txn = context.last_submitted_itxn.payment
    # Comparing Txn
    assert itxn_txn.sender == sender
