from collections.abc import Generator

from algopy import UInt64
import pytest
from algopy_testing import AlgopyTestContext, algopy_testing_context

from smart_contracts.counter.contract import Counter


@pytest.fixture()
def context() -> Generator[AlgopyTestContext, None, None]:
    with algopy_testing_context() as ctx:
        yield ctx
        ctx.reset()


def test_add(context: AlgopyTestContext) -> None:
    # Arrange
    # dummy_input = context.any_string()
    contract = Counter()

    # Act
    output_add = contract.add(UInt64(7),UInt64(8))
    assert output_add == 15

    output_sub = contract.sub(UInt64(10),UInt64(8))
    assert output_sub == 2
    
    # output_sub2 = contract.sub(UInt64(2),UInt64(8))
    # assert not output_sub2 
    
    output_mul = contract.mul(UInt64(2),UInt64(5))
    assert output_mul == 10
    
    output_div = contract.div(UInt64(20),UInt64(10))
    assert output_div == 2


    
    # Assert
    