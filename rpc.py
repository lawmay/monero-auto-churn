import json
import requests
import sys


headers = {'content-type': 'application/json'}
json_rpc_id = 0


def create_url(host, port):
    return 'http://' + host + ':' + str(port)


class RPC:
    def __init__(self, daemon_host='localhost', daemon_port=38081,
                 wallet_host='localhost', wallet_port=18082):
        self.daemon_host = daemon_host
        self.daemon_port = daemon_port
        self.daemon_url = create_url(daemon_host, daemon_port)

        self.wallet_host = wallet_host
        self.wallet_port = wallet_port
        self.wallet_url = create_url(wallet_host, wallet_port)

    def request(self, url, path, data):
        current_url = url + "/" + path

        try:
            return requests.post(current_url, data=json.dumps(data),
                                 headers=headers).json()
        except requests.exceptions.RequestException as error:
            print(error)
            sys.exit(1)

    def json_rpc_request(self, url, data):
        global json_rpc_id

        json_rpc_payload = {
            "id": json_rpc_id,
            "jsonrpc": "2.0",
        }

        json_rpc_payload.update(data)

        json_rpc_id += 1

        return self.request(url, "json_rpc", json_rpc_payload)

    """
    Wallet RPC calls
    """
    def get_accounts(self):
        payload = {
            "method": "get_accounts",
        }

        return self.json_rpc_request(self.wallet_url, data=payload)

    def create_account(self):
        payload = {
            "method": "create_account",
        }

        return self.json_rpc_request(self.wallet_url, data=payload)

    def sweep_all(self, account_index, amount, address):
        payload = {
            "method": "sweep_all",
            "params": {
                "account_index": account_index,
                "priority": 3,
                "ring_size": 7,
                "unlock_time": 0,
                "get_tx_key": True,
                "address": address,
            },
        }

        return self.json_rpc_request(self.wallet_url, data=payload)

    """
    Daemon RPC calls
    """
    def get_transactions(self, tx_hash):
        payload = {
            "txs_hashes": [
                tx_hash,
            ],
            "decode_as_json": True,
        }

        return self.request(self.daemon_url, "get_transactions", data=payload)

    def get_outs(self, indexes):
        outputs = []

        for index in indexes:
            outputs.append({"index": index})

        payload = {
            "outputs": outputs,
        }

        return self.request(self.daemon_url, "get_outs", data=payload)

    def get_block_header_by_height(self, block_height):
        payload = {
            "method": "get_block_header_by_height",
            "params": {
                "height": block_height,
            }
        }

        return self.json_rpc_request(self.daemon_url, data=payload)

