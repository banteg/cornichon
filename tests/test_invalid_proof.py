import brownie
from random import randrange


def test_wrong_amount(distributor, tree):
    idx = randrange(len(tree["claims"]))
    account = sorted(tree["claims"])[idx]
    claim = tree["claims"][account]

    with brownie.reverts("MerkleDistributor: Invalid proof."):
        distributor.claim(
            claim["index"], account, claim["amount"] + 1, claim["proof"],
        )


def test_wrong_index(distributor, tree):
    idx = randrange(len(tree["claims"]))
    account = sorted(tree["claims"])[idx]
    claim = tree["claims"][account]

    with brownie.reverts("MerkleDistributor: Invalid proof."):
        distributor.claim(
            claim["index"] + 1, account, claim["amount"], claim["proof"],
        )


def test_wrong_address(distributor, tree, deployer):
    idx = randrange(len(tree["claims"]))
    account = sorted(tree["claims"])[idx]
    claim = tree["claims"][account]

    with brownie.reverts("MerkleDistributor: Invalid proof."):
        distributor.claim(
            claim["index"], deployer, claim["amount"], claim["proof"],
        )
