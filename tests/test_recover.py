import pytest
from brownie import Wei, reverts, ZERO_ADDRESS


def test_owner_recovers_erc20_with_zero_amount(
    rewards_manager, ldo_token, manager_owner, ldo_holder
):
    rewards_amount = Wei("1 ether")
    ldo_token.transfer(rewards_manager, rewards_amount, {"from": ldo_holder})
    balance_before = ldo_token.balanceOf(manager_owner)
    tx = rewards_manager.recover_erc20(ldo_token, 0, {"from": manager_owner})
    assert len(tx.events) == 0

    balance_after = ldo_token.balanceOf(manager_owner)
    assert balance_before == balance_after
    assert ldo_token.balanceOf(rewards_manager) == rewards_amount


def test_owner_recovers_erc20_with_zero_recipient(
    rewards_manager, ldo_token, manager_owner, ldo_holder
):
    rewards_amount = Wei("1 ether")

    ldo_token.transfer(rewards_manager, rewards_amount, {"from": ldo_holder})

    with reverts("zero address not allowed"):
        rewards_manager.recover_erc20(
            ldo_token, 0, ZERO_ADDRESS, {"from": manager_owner}
        )


def test_owner_recovers_erc20_with_balance(
    rewards_manager, ldo_token, manager_owner, stranger, ldo_holder
):
    recipient = stranger
    transfer_amount = Wei("1 ether")
    recover_amount = Wei("0.5 ether")
    ldo_token.transfer(rewards_manager, transfer_amount, {"from": ldo_holder})
    assert ldo_token.balanceOf(rewards_manager) == transfer_amount

    recipient_balance_before = ldo_token.balanceOf(recipient)
    tx = rewards_manager.recover_erc20(
        ldo_token, recover_amount, recipient, {"from": manager_owner}
    )
    recipient_balance_after = ldo_token.balanceOf(recipient)

    assert ldo_token.balanceOf(rewards_manager) == transfer_amount - recover_amount
    assert recipient_balance_after - recipient_balance_before == recover_amount


def test_owner_recovers_erc20_to_the_caller_by_default(
    rewards_manager, ldo_token, manager_owner, ldo_holder
):
    transfer_amount = Wei("1 ether")
    ldo_token.transfer(rewards_manager, transfer_amount, {"from": ldo_holder})

    recipient_balance_before = ldo_token.balanceOf(manager_owner)
    tx = rewards_manager.recover_erc20(
        ldo_token, transfer_amount, {"from": manager_owner}
    )
    recipient_balance_after = ldo_token.balanceOf(manager_owner)

    assert ldo_token.balanceOf(rewards_manager) == 0
    assert recipient_balance_after - recipient_balance_before == transfer_amount


def test_recover_erc20_not_enough_balance(
    rewards_manager, ldo_token, manager_owner, ldo_holder
):
    transfer_amount = Wei("1 ether")
    recover_amount = Wei("2 ether")
    ldo_token.transfer(rewards_manager, transfer_amount, {"from": ldo_holder})

    with reverts("ERC20: transfer amount exceeds balance"):
        rewards_manager.recover_erc20(
            ldo_token, recover_amount, {"from": manager_owner}
        )


def test_owner_recovers_usdt_with_balance(
    rewards_manager, manager_owner, stranger, usdt_holder, usdt_token
):
    recipient = stranger
    transfer_amount = 10**8
    recover_amount = transfer_amount / 2
    usdt_token.transfer(rewards_manager, transfer_amount, {"from": usdt_holder})
    assert usdt_token.balanceOf(rewards_manager) == transfer_amount

    recipient_balance_before = usdt_token.balanceOf(recipient)
    tx = rewards_manager.recover_erc20(
        usdt_token, recover_amount, recipient, {"from": manager_owner}
    )
    recipient_balance_after = usdt_token.balanceOf(recipient)

    assert usdt_token.balanceOf(rewards_manager) == transfer_amount - recover_amount
    assert recipient_balance_after - recipient_balance_before == recover_amount
