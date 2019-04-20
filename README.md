
## monero-auto-churn

> Programmatically churn your monero


### Motivation

Statistical analysis is degrades privacy on the Monero network. Users have begun **churning** their own funds to mitigate the effects of blockchain analysis.


### Churning

Churning is process of sending your funds back to yourself. It is used to increase privacy at the cost *transaction* fees and *time*. However, churning can be detrimental if **best practices** are not followed.

If churning is done incorrectly, one *risks exposing themselves further* or *losing all their funds*.


The goal of this project is to automate this process.


### Goal
Automate the churning process using best practices.


### Best Practices
- Churn within a specified range (3-10)
- Use ring signature algorithm to gather timings
- Churn within own wallet


### Installation
```
pip install -r requirements.txt
```


### Future Improvements
- UTXO individually
- Coinbase outputs only
- Create wallets on the fly
- Logging
- Dummy transaction to get ring members not associated with a real transaction

