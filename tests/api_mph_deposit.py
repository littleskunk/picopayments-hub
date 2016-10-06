import os
import json
import shutil
import unittest
import tempfile
import jsonschema
from picopayments import api
from picopayments_client import auth
from picopayments import lib
from picopayments import srv
from picopayments import err
from picopayments_client import util
from picopayments_client.scripts import compile_deposit_script


CP_URL = os.environ.get("COUNTERPARTY_URL", "http://139.59.214.74:14000/api/")


DEPOSIT_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "deposit_script": {"type": "string"},
        "next_revoke_secret_hash": {"type": "string"},
        "signature": {"type": "string"},
        "pubkey": {"type": "string"},
    },
    "required": [
        "deposit_script", "next_revoke_secret_hash", "signature", "pubkey"
    ],
    "additionalProperties": False
}


class TestMpcHubDeposit(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp(prefix="picopayments_test_")
        self.basedir = os.path.join(self.tempdir, "basedir")
        shutil.copytree("tests/fixtures", self.basedir)
        srv.main([
            "--testnet",
            "--basedir={0}".format(self.basedir),
            "--cp_url={0}".format(CP_URL)
        ], serve=False)
        with open(os.path.join(self.basedir, "data.json")) as fp:
            self.data = json.load(fp)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_standard_usage_xcp(self):

        asset = "XCP"
        client_key = lib.create_key(asset, netcode="XTN")
        client_pubkey = client_key["pubkey"]

        h2c_spend_secret = util.b2h(os.urandom(32))
        h2c_spend_secret_hash = util.hash160hex(h2c_spend_secret)

        params = {
            "asset": asset,
            "spend_secret_hash": h2c_spend_secret_hash
        }
        params = auth.sign_json(params, client_key["wif"])
        result = api.mph_request(**params)

        handle = result["handle"]
        hub_pubkey = result["pubkey"]
        c2h_spend_secret_hash = result["spend_secret_hash"]

        c2h_deposit_script = compile_deposit_script(
            client_pubkey, hub_pubkey, c2h_spend_secret_hash, 1337
        )

        next_revoke_secret_hash = util.hash160hex(util.b2h(os.urandom(32)))
        params = {
            "handle": handle,
            "deposit_script": c2h_deposit_script,
            "next_revoke_secret_hash": next_revoke_secret_hash
        }
        params = auth.sign_json(params, client_key["wif"])
        result = api.mph_deposit(**params)

        self.assertIsNotNone(result)
        jsonschema.validate(result, DEPOSIT_RESULT_SCHEMA)

    def test_validate_deposit_not_already_given(self):

        def func():

            asset = "XCP"
            client_key = lib.create_key(asset, netcode="XTN")
            client_pubkey = client_key["pubkey"]

            h2c_spend_secret = util.b2h(os.urandom(32))
            h2c_spend_secret_hash = util.hash160hex(
                h2c_spend_secret
            )

            params = {
                "asset": asset,
                "spend_secret_hash": h2c_spend_secret_hash
            }
            params = auth.sign_json(params, client_key["wif"])
            result = api.mph_request(**params)

            handle = result["handle"]
            hub_pubkey = result["pubkey"]
            c2h_spend_secret_hash = result["spend_secret_hash"]

            c2h_deposit_script = compile_deposit_script(
                client_pubkey, hub_pubkey, c2h_spend_secret_hash, 1337
            )

            # submit deposit
            next_revoke_secret_hash = util.hash160hex(util.b2h(os.urandom(32)))

            params = {
                "handle": handle,
                "deposit_script": c2h_deposit_script,
                "next_revoke_secret_hash": next_revoke_secret_hash
            }
            params = auth.sign_json(params, client_key["wif"])
            result = api.mph_deposit(**params)
            self.assertIsNotNone(result)

            # resubmit deposit
            next_revoke_secret_hash = util.hash160hex(util.b2h(os.urandom(32)))
            params = {
                "handle": handle,
                "deposit_script": c2h_deposit_script,
                "next_revoke_secret_hash": next_revoke_secret_hash
            }
            params = auth.sign_json(params, client_key["wif"])
            result = api.mph_deposit(**params)

        self.assertRaises(err.DepositAlreadyGiven, func)

    def test_validate_handle_exists(self):

        def func():

            asset = "XCP"
            client_key = lib.create_key(asset, netcode="XTN")
            next_revoke_secret_hash = util.hash160hex(util.b2h(os.urandom(32)))
            c2h_deposit_script = util.b2h(os.urandom(32)),

            params = {
                "handle": "deadbeef",
                "deposit_script": c2h_deposit_script,
                "next_revoke_secret_hash": next_revoke_secret_hash
            }
            params = auth.sign_json(params, client_key["wif"])
            api.mph_deposit(**params)

        self.assertRaises(err.HandleNotFound, func)


if __name__ == "__main__":
    unittest.main()