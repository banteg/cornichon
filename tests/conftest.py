import json
import pytest


@pytest.fixture(autouse=True)
def isolation_setup(fn_isolation):
    # enable function isolation
    pass


@pytest.fixture(scope='module')
def deployer(accounts):
    return accounts[0]


@pytest.fixture(scope='module')
def cornichon(Cornichon, tree, deployer):
    return Cornichon.deploy("Cornichon", "CORN", tree["tokenTotal"], {"from": deployer})


@pytest.fixture(scope='module')
def tree():
    with open("snapshot/04-merkle.json") as fp:
        claim_data = json.load(fp)
    for value in claim_data["claims"].values():
        value["amount"] = int(value["amount"], 16)

    return claim_data


@pytest.fixture(scope='module')
def distributor(MerkleDistributor, tree, cornichon, deployer):
    contract = MerkleDistributor.deploy(
        cornichon, tree["merkleRoot"], {"from": deployer}
    )
    cornichon.transfer(contract, tree["tokenTotal"])

    return contract
