from collections.abc import Generator

import pytest
from algopy_testing import AlgopyTestContext, algopy_testing_context

from smart_contracts.marketplace.contract import Marketplace


@pytest.fixture()
def context() -> Generator[AlgopyTestContext, None, None]:
    with algopy_testing_context() as ctx:
        yield ctx
        ctx.reset()


def test_hello(context: AlgopyTestContext) -> None:
    # Arrange
    dummy_input = context.any_string()
    contract = Marketplace()

    # Act
    output = contract.hello(dummy_input)

    # Assert
    assert output == f"Hello, {dummy_input}"
