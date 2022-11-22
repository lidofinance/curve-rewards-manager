import os
import sys
from typing import Optional
from brownie import network, accounts


def network_name() -> Optional[str]:
    if network.show_active() is not None:
        return network.show_active()
    cli_args = sys.argv[1:]
    net_ind = next(
        (cli_args.index(arg) for arg in cli_args if arg == "--network"), len(cli_args)
    )

    net_name = None
    if net_ind != len(cli_args):
        net_name = cli_args[net_ind + 1]

    if net_name == None:
        return "mainnet"

    return net_name


if network_name() in ("optimism", "optimism-fork"):
    print(f"Using config_optimism.py addresses")
    from utils.config_optimism import *
elif network_name() in ("arbitrum", "arbitrum-fork"):
    print(f"Using arbitrum.py addresses")
    from utils.config_arbitrum import *
else:
    raise EnvironmentError(f"{network_name()} is not supported")


min_rewards_amount = 5000 * 10**18


def get_is_live():
    return network.show_active() != "development"


def get_env(name, is_required=True, message=None, default=None):
    if name not in os.environ:
        if is_required:
            raise EnvironmentError(message or f"Please set {name} env variable")
        else:
            return default
    return os.environ[name]


def get_deployer_account(is_live):
    if is_live and "DEPLOYER" not in os.environ:
        raise EnvironmentError(
            "Please set DEPLOYER env variable to the deployer account name"
        )

    deployer = (
        accounts.load(os.environ["DEPLOYER"])
        if is_live or "DEPLOYER" in os.environ
        else accounts[0]
    )

    return deployer


def prompt_bool():
    choice = input().lower()
    if choice in {"yes", "y"}:
        return True
    elif choice in {"no", "n"}:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")
