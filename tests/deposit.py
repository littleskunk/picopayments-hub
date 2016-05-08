import unittest
import picopayments


ASSET = "A14456548018133352000"
PAYER_WIF = "cT5RVbfLsgdUv2EAmbckFXNcsj9EmdAVvU9m6aarXb3fUpt9xkjX"
PAYEE_WIF = "cNk9V4XRrJisyHLvbNz5fmkD4DjuC1ZH4DppMGsrivpp8ipbfQs4"
USER = "rpc"
PASSWORD = "1234"
API_URL = "http://127.0.0.1:14000/api/"
TESTNET = True
DRYRUN = True


PAYEE_PUBKEY = ("0327f017c35a46b759536309e6de256ad"
                "44ad609c1c4aed0e2cdb82f62490f75f8")
SPEND_SECRET_HASH = "a7ec62542b0d393d43442aadf8d55f7da1e303cb"
EXPIRE_TIME = 5  # payer chooses expire time
EXPECTED = {
  "asset": "A14456548018133352000",
  "rawtx": (
    "0100000001dab5588f6df29b3f3b650f57b443bb2dbd9ba8d113dbf1f80b18b60f1a71"
    "0447000000006b483045022100ba5366aa8f8110ae52bc6ed3916ca1fcf86e7c11d621"
    "9dc398ecda528a0e4c6c02205f7e4b6177ff6a8f526fcb7ce946a70dbb0d356ca29eeb"
    "a665e90fd2a2a2889c0121033faa57e0ed3a3bf89340a0a3074ce0ef403ebfb77cb340"
    "2d0daa29d808e2bde0ffffffff03d2b400000000000017a914aa6d4750bb4db850b48e"
    "e784c5ad275f235b7f768700000000000000001e6a1cd9a71f04d5096e06527153002f"
    "7a950091739ca38e74120a36361f565e310200000000001976a914e960d8c0c0d4ee53"
    "6912b4e115fb8b8d84d5330b88ac00000000"
  ),
  "script": (
    "OP_IF OP_2 033faa57e0ed3a3bf89340a0a3074ce0ef403ebfb77cb3402d0daa29d80"
    "8e2bde0 0327f017c35a46b759536309e6de256ad44ad609c1c4aed0e2cdb82f62490f"
    "75f8 OP_2 OP_CHECKMULTISIG OP_ELSE OP_IF OP_HASH160 a7ec62542b0d393d43"
    "442aadf8d55f7da1e303cb OP_EQUALVERIFY 033faa57e0ed3a3bf89340a0a3074ce0"
    "ef403ebfb77cb3402d0daa29d808e2bde0 OP_CHECKSIG OP_ELSE OP_5 OP_NOP3 OP"
    "_DROP 033faa57e0ed3a3bf89340a0a3074ce0ef403ebfb77cb3402d0daa29d808e2bd"
    "e0 OP_CHECKSIG OP_ENDIF OP_ENDIF"
  ),
  "txid": "9a602185541095aac7e59b7d6942a800aef6358e0dee5004a9cdfb085a9908a5",
  "quantity": 1337,
  "address": "2N8nMmhmPoxTXckZV2h9HvcNedmjB65LzBz"
}


class TestDeposit(unittest.TestCase):

    def setUp(self):
        self.channel = picopayments.channel.Payer(
            ASSET, api_url=API_URL, testnet=TESTNET, dryrun=DRYRUN
        )

    def tearDown(self):
        self.channel.stop()

    def test_deposit(self):
        self.channel.initialize(PAYER_WIF, PAYEE_PUBKEY,
                                SPEND_SECRET_HASH, EXPIRE_TIME)
        deposit_info = self.channel.deposit(1337)
        self.assertEqual(EXPECTED, deposit_info)


if __name__ == "__main__":
    unittest.main()
