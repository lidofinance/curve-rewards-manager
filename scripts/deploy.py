from copyreg import constructor
import sys
from brownie import RewardsManager, network
import json

from utils.config import (
    manager_owner_address,
    rewards_contract_address,
    min_rewards_amount,
    ldo_token_address,
    get_is_live,
    get_deployer_account,
    prompt_bool,
)


def main():
    is_live = get_is_live()
    deployer = get_deployer_account(is_live)
    rewards_contract = rewards_contract_address
    rewards_token = ldo_token_address

    print(f"Deployer: {deployer}")
    print(f"REWARDS CONTRACT: {rewards_contract}")
    print(f"LDO TOKEN: {rewards_token}")
    print(f"OWNER: {manager_owner_address}")
    print(f"MINIMAL REWARDS AMOUNT: {min_rewards_amount} ({min_rewards_amount / 1e18})")
    sys.stdout.write("Proceed? [y/n]: ")

    if not prompt_bool():
        print("Aborting")
        return

    tx_params = {"from": deployer, "priority_fee": "3 gwei"}
    if not is_live:
        del tx_params["priority_fee"]

    manager_contract = RewardsManager.deploy(
        manager_owner_address,
        min_rewards_amount,
        rewards_contract,
        rewards_token,
        tx_params,
    )

    with open(f"deployed-{network.show_active()}.json", "w") as f:
        json.dump(
            {
                "networkId": network.chain.id,
                "curveRewardsManager": {
                    "constructorParams": [
                        manager_owner_address,
                        min_rewards_amount,
                        rewards_contract,
                        rewards_token,
                    ],
                    "baseAddress": manager_contract.address,
                    "tx": manager_contract.tx.txid,
                },
            },
            f,
        )

    print("Manager contract: ", manager_contract)
