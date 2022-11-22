import pytest
from brownie import accounts, LiquidityGaugeMock, RewardsManager

from utils.config import (
    rewards_contract_address,
    usdt_token_address,
    usdt_holder_address,
    ldo_holder_address,
    manager_owner_address,
    ldo_token_address,
    curve_admin_address,
)


@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture(scope="module")
def deployer(accounts):
    return accounts[0]


@pytest.fixture(scope="module")
def stranger(accounts):
    return accounts[9]


@pytest.fixture(scope="module")
def ldo_token(interface):
    return interface.ERC20(ldo_token_address)


@pytest.fixture(scope="module")
def ldo_holder():
    return accounts.at(ldo_holder_address, force=True)


@pytest.fixture(scope="module")
def rewards_contract_mock(deployer):
    return LiquidityGaugeMock.deploy(deployer, ldo_token_address, {"from": deployer})


@pytest.fixture(scope="module")
def rewards_contract(interface):
    return interface.LiquidityGauge(rewards_contract_address)


@pytest.fixture(scope="module")
def curve_admin(accounts):
    return accounts.at(curve_admin_address, force=True)


@pytest.fixture(scope="module")
def manager_owner(accounts):
    return accounts.at(manager_owner_address, force=True)


@pytest.fixture(scope="module")
def rewards_manager(rewards_contract_mock, deployer, ldo_token, manager_owner):
    manager = RewardsManager.deploy(
        manager_owner, 10**18, rewards_contract_mock, ldo_token, {"from": deployer}
    )
    rewards_contract_mock.set_reward_distributor(ldo_token, manager, {"from": deployer})
    return manager


@pytest.fixture(scope="module")
def usdt_holder(accounts):
    return accounts.at(usdt_holder_address, force=True)


@pytest.fixture(scope="module")
def usdt_token(interface):
    return interface.ERC20(usdt_token_address)


class Helpers:
    @staticmethod
    def filter_events_from(addr, events):
        return list(filter(lambda evt: evt.address == addr, events))

    @staticmethod
    def assert_single_event_named(evt_name, tx, evt_keys_dict):
        receiver_events = Helpers.filter_events_from(tx.receiver, tx.events[evt_name])
        assert len(receiver_events) == 1
        assert dict(receiver_events[0]) == evt_keys_dict


@pytest.fixture(scope="module")
def helpers():
    return Helpers
