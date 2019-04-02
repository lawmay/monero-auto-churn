#!/usr/bin/env python3

from rpc import RPC
import utils


def print_accounts(accounts):
    for i, account in enumerate(accounts):
        print("{}:".format(i), account["base_address"])
        print("\tunlocked balance:\t{}".format(utils.convert_to_monero(account["unlocked_balance"])))
        print("\tbalance:\t\t{}".format(utils.convert_to_monero(account["balance"])))

        locked_balance = account["balance"] - account["unlocked_balance"]
        print("\tlocked balance:\t\t{}".format(utils.convert_to_monero(locked_balance)))

        print()


def main():
    rpc = RPC()

    response = rpc.get_accounts()
    accounts = response["result"]["subaddress_accounts"]
    print("\nTotal accounts:", len(accounts), "\n")

    print_accounts(accounts)


if __name__ == "__main__":
    main()

