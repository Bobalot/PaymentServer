from pybitcointools import deterministic
from pybitcointools.main import bin_to_b58check
from binascii import unhexlify
from redis import Redis
import requests


# This is not advisable to use, as you could reveal your entire address set to blockchain.info
def bci_scan_addresses(mpk, gap_limit=50, addresses_per_request=50):
    n = 0
    empty_count = 0
    utxo_list = []

    #Address mapping is a dict of address:idx
    address_mapping = {}

    while True:
        serialized_addresses = ""

        # Send multiple addresses at once to bci, to limit number of requests.
        for i in range(addresses_per_request):
            n += 1
            address = deterministic.electrum_address(mpk, n)
            address_mapping[address] = n

            serialized_addresses += address

            if i < addresses_per_request:
                serialized_addresses += "|"

        req = requests.get("http://blockchain.info/unspent?active=" + serialized_addresses)

        if req.status_code == 200:
            bci_utxo = req.json()['unspent_outputs']

            for utxo in bci_utxo:
                address = script_extract_address(unhexlify(utxo['script']))
                address_index = address_mapping[address]

                utxo_list.append({"address_index": address_index,
                                  "address": address,
                                  "value": utxo['value'],
                                  "tx_hash": utxo['tx_hash'],
                                  "n": utxo['tx_output_n']})

        # bci returns status code 500, when there are no unspent outputs.
        else:
            empty_count += addresses_per_request

        if empty_count > gap_limit:
            break

    return utxo_list

OP_DUP = chr(0x76)
OP_HASH160 = chr(0xA9)
OP_EQUALVERIFY = chr(0x88)
OP_CHECKSIG = chr(0xAC)


def script_extract_address(script):
    # very simple, check for OP_DUP OP_HASH160 0x14 <pubkey hash> OP_EQUALVERIFY OP_CHECKSIG
    if script[0] != OP_DUP or script[1] != OP_HASH160 or script[-2] != OP_EQUALVERIFY or script[-1] != OP_CHECKSIG:
        return False

    # turn hash into address
    pubkey_hash = script[3:23]
    return bin_to_b58check(pubkey_hash)


def obelisk_scan_addresses(mpk, gap_limit=5):
    raise NotImplementedError


def last_n_used():
    from config import redis_prefix, index_key
    r = Redis()
    return r.get(redis_prefix + index_key)

if __name__ == "__main__":
    from config import mpk
    print bci_scan_addresses(mpk, gap_limit=100)