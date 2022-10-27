# Curve liquidity gauge manager

This repository contains rewards manager for Curve Liquidity Gauge. The manager simplifies reward distribution operations by DAO voting and Easy Track.

[Optimism Curve Liquidity Gauge](https://optimistic.etherscan.io/address/0xD53cCBfED6577d8dc82987e766e75E3cb73a8563)

[Arbitrum Curve Liquidity Gauge](https://arbiscan.io/address/0x098EF55011B6B8c99845128114A9D9159777d697)

## Environment preparation with Poetry

Step 1. Install dependencies
```shell
poetry install
```

Step 2. Install Ganache locally

Simply run the following command from the project's directory

```shell
yarn
```

Step 3. Import network config to connect brownie with local Ganache

```shell
poetry run brownie networks import network-config.yaml True
```

Step 4. Activate virtual environment

```shell
poetry shell
```

## Testing

`brownie test -s`

## Deploying Environment

The `deploy.py` script is in charge of the `RewardsManager` contract on-chain deployment.
The following environment variables needs to be set for the script's execution:

* `DEPLOYER` - deployer account

## Specification

#### [RewardsManager.vy](contracts/RewardsManager.vy)

**def period_finish() -> uint256: view**

Returns estimated date of last rewards period start date
    
    CLG.periodFinish + (WEEKS_PER_PERIOD - self.rewards_iteration ) % WEEKS_PER_PERIOD * SECONDS_PER_WEEK
    
**def start_next_rewards_period()**

Permissionless method, allows to start new weekly rewards period at Curve Liquidity Gauge

If contact has enough assets in it (`LDO.balanceOf(self) >= self.weekly_amount`), and the CLG period is finished, it will start a new period by calling `deposit_reward_token(_reward_token: address, _amount: uint256): nonpayable` with `self.weekly_amount` as amount of LDO

Recalculates `self.weekly_amount` every 4 calls, requires balance to be not less then `self.min_rewards_amount`

Events:

```vyper=
event NewRewardsPeriodStarted:
    amount: uint256
```

```vyper=
event WeeklyRewardsAmountUpdated:
    newWeeklyRewardsAmount: uint256
```

**def replace_me_by_other_distributor(_to: address):**

Transfers permission to start new rewards period form self.

Events:

```vyper=
event RewardsContractTransferred:
    newDistributor: indexed(address)
```

**def recover_erc20(_token: address, _amount: uint256, _recipient: address = msg.sender):**

Transfers the amount of the given ERC20 token to the recipient. Can be called by owner only.

Events:
```vyper=
event ERC20TokenRecovered:
    token: indexed(address)
    amount: uint256
    recipient: indexed(address)
```
