import os
import logging

from fireblocks_defi_sdk_py.web3_bridge import Web3Bridge
from fireblocks_defi_sdk_py.chain import Chain
from fireblocks_sdk import FireblocksSDK
from google.cloud import secretmanager

from util import get_web3, read_abi


class Trade:
    def __init__(self, trade_id: str, network: str, user: str):
        self.trade_id = trade_id
        self.network = network
        self.w3 = get_web3(network)
        self.user = user
        self.fb = self.setup_fireblocks()

    def ensure_approval(self, user, token, target, amount):
        contract = self.w3.eth.contract(
            token, abi=(read_abi(os.getenv("ERC20"), "token"))
        )
        allowance = contract.functions.allowance(user, target).call()
        logging.info(f"Current allowance: {allowance}, required allowance: {amount}")
        if allowance > amount:
            logging.info("Allowance OK")
            return True
        else:
            logging.error(f"Wallet: {user}")
            logging.error(f"token: {token}")
            logging.error(f"target: {target}")
            raise ValueError(
                f"Not Enough allowance for {user} to spend {token} at {target}"
            )

    def setup_fireblocks(self):
        if self.test:
            secret_key_id = "projects/712543440434/secrets/fireblocks_secret_key_test/versions/latest"
            secret_api_id = (
                "projects/712543440434/secrets/fireblocks_api_key_test/versions/latest"
            )
        else:
            secret_key_id = (
                "projects/712543440434/secrets/fireblocks_secret_key/versions/latest"
            )
            secret_api_id = (
                "projects/712543440434/secrets/fireblocks_api_key/versions/latest"
            )

        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(request={"name": secret_key_id})
        fireblocks_secret_key = response.payload.data.decode("UTF-8")

        response = client.access_secret_version(request={"name": secret_api_id})
        fireblocks_api_key = response.payload.data.decode("UTF-8")
        return FireblocksSDK(fireblocks_secret_key, fireblocks_api_key)

    def get_fb_bridge(self):
        network = self.network
        if network == "polygon":
            chain = Chain.POLYGON
            vault_account_id = "4"
        elif network == "ropsten":
            chain = Chain.ROPSTEN
            vault_account_id = "1"
        fb_bridge = Web3Bridge(
            fb_api_client=self.fb,
            vault_account_id=vault_account_id,  # os.environ.get("FIREBLOCKS_SOURCE_VAULT_ACCOUNT"),
            chain=chain,
        )
        return fb_bridge

    def send_transaction_fireblocks(self, tx):
        logging.debug(f"simulating transaction")
        sim_res = tx.call({"from": self.user})
        logging.debug(f"result: {sim_res}")
        logging.debug("sending transaction")
        if self.send_tx:
            tx_raw = tx.buildTransaction({"from": self.user})
            fb_bridge = self.get_fb_bridge()
            try:
                tx_result = fb_bridge.send_transaction(tx_raw, test=self.test)
            except Exception as e:
                logging.error(f"Failed sending fireblocks transaction")
                logging.error(e)
                raise ConnectionError()

            return fb_bridge.check_tx_is_completed(tx_result["id"])
        else:
            return sim_res
