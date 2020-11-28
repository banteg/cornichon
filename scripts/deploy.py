import json
from brownie import MerkleDistributor, Cornichon, accounts, rpc, interface, Contract


def main():
    tree = json.load(open("snapshot/04-merkle.json"))
    user = accounts[0] if rpc.is_active() else accounts.load(input("account: "))
    root = tree["merkleRoot"]
    cornichon = Cornichon.deploy(
        "Cornichon", "CORN", tree["tokenTotal"], {"from": user}
    )
    distributor = MerkleDistributor.deploy(cornichon, root, {"from": user})
    cornichon.transfer(distributor, cornichon.balanceOf(user))
