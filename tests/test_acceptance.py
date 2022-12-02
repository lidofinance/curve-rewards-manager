import pytest
from brownie import chain, RewardsManager, reverts
from math import floor
from utils.config import network_name
from os.path import exists
import json

rewards_period = 3600 * 24 * 7
rewards_amount = 5_000 * 10**18


def test_acceptance(
    ldo_token,
    stranger,
    rewards_contract,
    helpers,
    accounts,
    ldo_holder,
):
    deployment_file_path = f"deployed-{network_name().replace('fork', 'main')}.json"

    if not exists(deployment_file_path):
        pytest.skip(f"no RewardsManager deployed on {network_name()}")

    chain.sleep(3600 * 24 * 7)
    chain.mine()

    f = open(deployment_file_path, "r")
    deployment_data = json.load(f)
    rewards_manager = RewardsManager.at(
        deployment_data["curveRewardsManager"]["baseAddress"]
    )
    f.close()

    balance_before = ldo_token.balanceOf(rewards_contract)

    reward_data = rewards_contract.reward_data(ldo_token)
    if reward_data[0] != rewards_manager:
        current_distributor = accounts.at(reward_data[0], {"force": True})
        rewards_contract.set_reward_distributor(
            ldo_token, rewards_manager, {"from": current_distributor}
        )
    reward_data = rewards_contract.reward_data(ldo_token)

    assert reward_data[0] == rewards_manager
    assert reward_data[1] == rewards_manager.period_finish()

    for month in range(2):
        with reverts("manager: low balance"):
            rewards_manager.start_next_rewards_period({"from": stranger})

        ldo_token.transfer(rewards_manager, 4 * rewards_amount, {"from": ldo_holder})
        balance_before = ldo_token.balanceOf(rewards_contract)

        reward_data = rewards_contract.reward_data(ldo_token)
        assert reward_data[1] == rewards_manager.period_finish()

        assert rewards_manager.is_curve_rewards_period_finished() == True

        tx = rewards_manager.start_next_rewards_period({"from": stranger})

        assert rewards_manager.is_curve_rewards_period_finished() == False

        reward_data = rewards_contract.reward_data(ldo_token)
        assert reward_data[1] + rewards_period * 3 == rewards_manager.period_finish()

        helpers.assert_single_event_named(
            "NewRewardsPeriodStarted", tx, {"amount": rewards_amount}
        )

        helpers.assert_single_event_named(
            "WeeklyRewardsAmountUpdated", tx, {"newWeeklyRewardsAmount": rewards_amount}
        )

        chain.sleep(rewards_period - 10)
        chain.mine()

        assert rewards_manager.is_curve_rewards_period_finished() == False

        with reverts("manager: rewards period not finished"):
            rewards_manager.start_next_rewards_period({"from": stranger})

        assert ldo_token.balanceOf(rewards_contract) == balance_before + rewards_amount

        chain.sleep(10)
        chain.mine()

        for week in range(3):

            reward_data = rewards_contract.reward_data(ldo_token)
            assert (
                reward_data[1] + rewards_period * (3 - week)
                == rewards_manager.period_finish()
            )

            balance_before = ldo_token.balanceOf(rewards_contract)

            assert rewards_manager.is_curve_rewards_period_finished() == True

            tx = rewards_manager.start_next_rewards_period({"from": stranger})

            assert rewards_manager.is_curve_rewards_period_finished() == False

            reward_data = rewards_contract.reward_data(ldo_token)
            assert (
                reward_data[1] + rewards_period * (3 - week - 1)
                == rewards_manager.period_finish()
            )

            helpers.assert_single_event_named(
                "NewRewardsPeriodStarted", tx, {"amount": rewards_amount}
            )

            chain.sleep(rewards_period - 10)
            chain.mine()

            assert rewards_manager.is_curve_rewards_period_finished() == False

            with reverts("manager: rewards period not finished"):
                rewards_manager.start_next_rewards_period({"from": stranger})

            assert (
                ldo_token.balanceOf(rewards_contract) == balance_before + rewards_amount
            )

            chain.sleep(10)
            chain.mine()
