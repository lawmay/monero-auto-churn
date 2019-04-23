
## monero-auto-churn

> Programmatically churn your monero


### Motivation

Statistical analysis is degrades privacy on the Monero network. Users have begun **churning** their own funds to mitigate the effects of blockchain analysis.


### Churning

Churning is process of sending your funds back to yourself. It is used to increase privacy at the cost of *transaction fees* and *time*. However, churning can be detrimental if **best practices** are not followed.

If churning is done incorrectly, one *risks exposing themselves further* or *losing all their funds*.


The goal of this project is to automate this process.


### Goal
Automate the churning process using best practices.


### Best Practices
- Churn within a specified range (3-10)
- Use ring signature algorithm to gather timings
- Churn within own wallet

### Algorithm

#### *Churn destinations*
The process starts by churning all funds from other accounts to account **1** and progressively increase. The last churn will move all funds back to account **0**.

#### *Churn intervals*
The transaction hash for the first churn (to account **1**) is used to gather a list of ring members. The timings between those ring members are used to determine the intervals between churns.

To describe in further detail:
1. UTXOs in the ring are calculated from the transaction hash.
2. Get block heights of each UTXO.
3. Get timestamp of each block.
4. The time difference between each successive ring member (chronologically from most recent) is calculated and used as the wait time between churns.

**NOTE**: A randomize minimum range (in seconds) is added to each interval to account for adjacent ring members that are in the same block.


### Installation
```
$ pip install -r requirements.txt
```

**NOTE**: You can create a **python3** virtual environment for this script using **python3**'s built-in virtual environment tool:
```
$ python3 -m venv ~/venv/[name]

$ source ~/venv/[name]/bin/activate
```
Then run the `pip install` above. To leave the virutal environment, type `deactivate`.


### Usage
List script options:
```
$ ./churn.py --help
```

A utility script is included called `view.py`. This let's you see the balance of your Monero wallet. Just make sure you've opened a wallet with the `monero-wallet-rpc` server (not a wallet directory.)

### Future Improvements
- UTXO individually
- Coinbase outputs only
- Create wallets on the fly
- Logging
- Create a dummy transaction to get ring members not associated with a real transaction

