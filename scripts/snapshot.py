import json
import os
from collections import Counter
from fractions import Fraction
from functools import wraps
from itertools import zip_longest
from pathlib import Path

from brownie import MerkleDistributor, Wei, accounts, chain, interface, web3
from eth_abi.packed import encode_abi_packed
from eth_utils import encode_hex
from tqdm import trange

snapshot_block = 11303122  # one block before exploit https://ethtx.info/mainnet/0xe72d4e7ba9b5af0cf2a8cfb1e30fd9f388df0ab3da79790be842bfbed11087b0
pdai = interface.PickleJar("0x6949Bb624E8e8A90F87cD2058139fcd77D2F3F87")
chef = interface.PickleChef("0xbD17B1ce622d73bD438b9E658acA5996dc394b0d")
pool_id = 16
pdai_deploy = 11044218  # https://etherscan.io/tx/0xc1ba30bd850ebd12213a61c4c2b58619ea0200a8293bace4148881fbe49cccc8
multicall = interface.Multicall("0xeefBa1e63905eF1D7ACbA5a8513c70307C1cE441")
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def main():
    in_jar = pdai_balances()
    in_chef = chef_balances(in_jar)
    balances = merge_balances(in_jar, in_chef)
    distribution = prepare_merkle_tree(balances)
    print("recipients:", len(balances))
    print("total supply:", sum(balances.values()) / 1e18)
    print("merkle root:", distribution["merkleRoot"])


def cached(path):
    path = Path(path)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if path.exists():
                print("load from cache", path)
                return json.load(path.open())
            else:
                result = func(*args, **kwargs)
                if result is None:
                    return
                os.makedirs(path.parent, exist_ok=True)
                json.dump(result, path.open("wt"), indent=2)
                print("write to cache", path)
                return result

        return wrapper

    return decorator


@cached("snapshot/01-pdai.json")
def pdai_balances():
    balances = transfers_to_balances(pdai, pdai_deploy, snapshot_block)
    balances.pop(str(chef))
    return balances


@cached("snapshot/02-chef.json")
def chef_balances(balances):
    calls = [(chef, chef.userInfo.encode_input(pool_id, user)) for user in balances]
    _, results = multicall.aggregate.call(calls, block_identifier=snapshot_block)
    data = {
        user: chef.userInfo.decode_output(data)[0]
        for user, data in zip(balances, results)
    }
    return dict(Counter(data).most_common())


@cached("snapshot/03-dai.json")
def merge_balances(in_jar, in_chef):
    data = Counter(in_jar) + Counter(in_chef)
    ratio = Fraction(pdai.getRatio(block_identifier=snapshot_block), 10 ** 18)
    data = {user: int(balance * ratio) for user, balance in data.items()}
    return dict(Counter(data).most_common())


@cached("snapshot/04-merkle.json")
def prepare_merkle_tree(balances):
    elements = [
        (index, account, amount)
        for index, (account, amount) in enumerate(balances.items())
    ]
    nodes = [
        encode_hex(encode_abi_packed(["uint", "address", "uint"], el))
        for el in elements
    ]
    tree = MerkleTree(nodes)
    distribution = {
        "merkleRoot": encode_hex(tree.root),
        "tokenTotal": hex(sum(balances.values())),
        "claims": {
            user: {
                "index": index,
                "amount": hex(amount),
                "proof": tree.get_proof(nodes[index]),
            }
            for index, user, amount in elements
        },
    }
    return distribution


def transfers_to_balances(contract, deploy_block, snapshot_block):
    balances = Counter()
    contract = web3.eth.contract(str(contract), abi=contract.abi)
    step = 10000
    for start in trange(deploy_block, snapshot_block, step):
        end = min(start + step - 1, snapshot_block)
        logs = contract.events.Transfer().getLogs(fromBlock=start, toBlock=end)
        for log in logs:
            if log["args"]["from"] != ZERO_ADDRESS:
                balances[log["args"]["from"]] -= log["args"]["value"]
            if log["args"]["to"] != ZERO_ADDRESS:
                balances[log["args"]["to"]] += log["args"]["value"]

    return dict(balances.most_common())


class MerkleTree:
    def __init__(self, elements):
        self.elements = sorted(set(web3.keccak(hexstr=el) for el in elements))
        self.layers = MerkleTree.get_layers(self.elements)

    @property
    def root(self):
        return self.layers[-1][0]

    def get_proof(self, el):
        el = web3.keccak(hexstr=el)
        idx = self.elements.index(el)
        proof = []
        for layer in self.layers:
            pair_idx = idx + 1 if idx % 2 == 0 else idx - 1
            if pair_idx < len(layer):
                proof.append(encode_hex(layer[pair_idx]))
            idx //= 2
        return proof

    @staticmethod
    def get_layers(elements):
        layers = [elements]
        while len(layers[-1]) > 1:
            layers.append(MerkleTree.get_next_layer(layers[-1]))
        return layers

    @staticmethod
    def get_next_layer(elements):
        return [
            MerkleTree.combined_hash(a, b)
            for a, b in zip_longest(elements[::2], elements[1::2])
        ]

    @staticmethod
    def combined_hash(a, b):
        if a is None:
            return b
        if b is None:
            return a
        return web3.keccak(b"".join(sorted([a, b])))
