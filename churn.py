#!/usr/bin/env python3 -u
#
# Programmatically churn funds between accounts in your Monero wallet

import argparse
import json
from progress.bar import Bar
import random
from rpc import RPC
import sys
import time
import utils


# Parameters
CHURNS = None
IS_DRY_RUN = False
IS_QUICK = False

# Random churn times
LOWER = 1234
UPPER = 2345
QUICK_LOWER = 3
QUICK_UPPER = 5

# Churn upper and lower limits
CHURN_LOWER = 3
CHURN_UPPER = 10

# Balances are locked for 10 blocks
# and a new block is mined roughly every 2min
# 10 block * 2 minutes * 60 seconds = 1200
MINIMUM_WAIT = 1200


def get_random_churns():
    return random.randrange(3, 11)

def get_dry_run_wait_times(churns, lower=LOWER, upper=UPPER, quick=False):
    if quick:
        lower = QUICK_LOWER
        upper = QUICK_UPPER

    return [random.randrange(lower, upper) for i in range(churns - 1)]

def print_accounts(accounts):
    for i, account in enumerate(accounts):
        print("{}:".format(i), account["base_address"])
        print("\tunlocked_balance:",
              round(utils.convert_to_monero(account["unlocked_balance"]), 2))
        print("\tbalance:",
              round(utils.convert_to_monero(account["balance"]), 2), "\n")

def print_wait_times(churns, wait_times):
    print("\n\nWAIT TIMES")
    print("-------------------------------------")
    print("For {} churns, we wait {} times".format(churns, churns - 1))

    total_seconds = 0

    for i, seconds in enumerate(wait_times):
        print("{} seconds ({} hr)".format(
                                   seconds,
                                   round(utils.seconds_to_hours(seconds), 1)))

        total_seconds += seconds

        if i == (churns - 2):
            break

    print("Total: {} seconds ({} hr)"
          .format(total_seconds,
                  round(utils.seconds_to_hours(total_seconds), 1)))

def get_wait_times_from_transaction(tx_hash, rpc):
    transactions = rpc.get_transactions(tx_hash)
    ring_member_offsets = []

    for tx_str in transactions["txs_as_json"]:
        tx = json.loads(tx_str)
        for vin in tx["vin"]:
            ring_member_offsets = vin["key"]["key_offsets"]
            break

    # Get transaction output ring members
    ring_members = []
    current_offset = 0

    for offset in ring_member_offsets:
        current_offset += offset
        ring_members.append(current_offset)

    # Get block height of each transaction output in the ring
    response = rpc.get_outs(ring_members)
    block_heights = [out["height"] for out in response["outs"]]

    # Get timestamp of each ring member's block
    block_timestamps = []

    for height in block_heights:
        block_header = rpc.get_block_header_by_height(height)
        block_timestamp = block_header["result"]["block_header"]["timestamp"]
        block_timestamps.append(block_timestamp)

    block_timestamps.sort(reverse=True)

    # Calculate block timestamp differences (and use those as churn timings)
    wait_times = [block_timestamps[i] - block_timestamps[i + 1] for i in range(len(block_timestamps) - 1)]

    # Add minimum waiting time for cases where block differences are lower
    # than the time it takes to unlock a balance
    # wait_times = [int((wait_time + MINIMUM_WAIT) / 10) for wait_time in wait_times]
    wait_times = [int(wait_time + MINIMUM_WAIT) for wait_time in wait_times]

    return wait_times

def sleep(seconds):
    print("\n\nSleeping for {} seconds ({} hr)"
          .format(seconds,
                  round(utils.seconds_to_hours(seconds), 1)))

    bar = Bar(max=seconds)

    while(seconds > 0):
        bar.next()
        time.sleep(1)
        seconds -= 1

def churn(accounts, destination_account, rpc, dry_run=True):
    print("------------------------------------------------------")

    current_account = accounts[destination_account]["base_address"]
    tx_hash = None

    for i, account in enumerate(accounts):
        balance = account["unlocked_balance"]

        if destination_account != i:
            if balance > 0:
                print("Transferring from account {} ({}) to account {}"
                      .format(i, round(utils.convert_to_monero(balance), 2), destination_account))

                response = None

                if not dry_run:
                      response = rpc.sweep_all(i, account["unlocked_balance"],
                                               current_account)

                      # We need a transaction hash to get churn times
                      if tx_hash is None:
                          tx_hash = response["result"]["tx_hash_list"][0]

                if response is not None and "result" in response and "tx_hash_list" in response["result"]:
                    print("Transaction hash:", response["result"]["tx_hash_list"][0])

                time.sleep(0.5)
            else:
                print("Nothing in account {} to transfer to account {}".format(i, destination_account))

    return tx_hash

def create_accounts(churns, total_accounts, rpc):
    churn_account_difference = churns - total_accounts

    if churn_account_difference > 0:
        print("We need to create more account in this wallet to churn with")

        for i in range(churn_account_difference):
            response = rpc.create_account()
            result = response["result"]
            print("Created a new account:")
            print("\taccount_index:", result["account_index"])
            print("\taddress:", result["address"])

        return True

    return False

def main():
    """
    Check if the number of churns passed in within our allowed range
    """
    if CHURNS < CHURN_LOWER:
        print("Can't churn less than {} times. Exiting...".format(CHURN_LOWER))
        sys.exit(1)
    elif CHURNS > CHURN_UPPER:
        print("Can't churn more than {} times. Exiting...".format(CHURN_UPPER))
        sys.exit(1)

    """
    Indicate whether it's a dry run
    """
    if IS_DRY_RUN:
        print()
        print("*********************************************")
        print("DRY RUN IN PROGRESS: FUNDS WILL NOT BE MOVED!")
        print("*********************************************")

    """
    Check if we need to create new accounts within the walllet
    """
    rpc = RPC()
    response = rpc.get_accounts()
    accounts = response["result"]["subaddress_accounts"]
    total_accounts = len(accounts)

    print("\nChurns: {}\tTotal accounts: {}\n".format(CHURNS, total_accounts))

    if create_accounts(CHURNS, total_accounts, rpc):
        # Re-fetch accounts
        response = rpc.get_accounts()
        accounts = response["result"]["subaddress_accounts"]


    """
    Sweep all to first account
    Grab a transaction hash, then get churn timings.
    The transaction hash is needed to get the churn times.
    """
    print("\nChurn 1")

    # Send all funds to first account
    # and grab tx_hash to get churn timings
    tx_hash = churn(accounts, 1, rpc, dry_run=IS_DRY_RUN)

    wait_times = []

    if tx_hash is not None:
        print("\n\nUsing transaction hash {} to get wait times".format(tx_hash))
        wait_times = get_wait_times_from_transaction(tx_hash, rpc)
    else:
        wait_times = get_dry_run_wait_times(CHURNS, quick=IS_QUICK)

    print_wait_times(CHURNS, wait_times)


    """
    Using the generated churn times: sleep, churn, repeat
    NOTE: First sweep_all counts as a churn.
    """
    for n in range(2, CHURNS):
        # Sleep first, then churn
        current_wait_time = wait_times[n - 2]
        sleep(current_wait_time)

        # Start a new churn
        print("\n\nChurn", n)
        churn(accounts, n, rpc, dry_run=IS_DRY_RUN)


    """
    Last churn, back to account 0
    """
    # Sleep first, then do the last churn
    current_wait_time = wait_times[len(wait_times) - 1]
    sleep(current_wait_time)

    # Transfer all back to main account
    print("\n\nLast churn ({})".format(CHURNS))

    churn(accounts, 0, rpc, dry_run=IS_DRY_RUN)


    """
    Exit when done
    """
    print("\n\nChurns completed successfully\n"
          "(It may take time for your balance to unlock from the last churn)\n")

    # print("Exiting...\n")
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", "-d", action="store_true",
                        help="run a dry run that doesn't move funds")
    parser.add_argument("--quick-dry-run", "-q", action="store_true",
                        help="do a quick version of a dry run")
    parser.add_argument("--churns", "-c", action="store", default=None,
                        help="set number of churns (between 2-10)")

    args = parser.parse_args()

    CHURNS = int(args.churns) if args.churns is not None else get_random_churns()

    if args.quick_dry_run:
        IS_DRY_RUN = True
        IS_QUICK = True
    elif args.dry_run:
        IS_DRY_RUN = True

    main()

