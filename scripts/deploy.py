import json
from brownie import MerkleDistributor, Cornichon, accounts, rpc


def main():
    tree = json.load(open("snapshot/04-merkle.json"))
    user = accounts[0] if rpc.is_active() else accounts.load(input("account: "))
    root = tree["merkleRoot"]
    cornichon = Cornichon.deploy('Cornichon', 'CHON', tree['tokenTotal'], {'from': user})
    distributor = MerkleDistributor.deploy(cornichon, root, {"from": user})
    cornichon.transfer(distributor, cornichon.balanceOf(user))
    if not rpc.is_active():
        return
    
    # test full distribution
    for user, claim in tree['claims'].items():
        distributor.claim(claim['index'], user, claim['amount'], claim['proof'])
        assert cornichon.balanceOf(user) == claim['amount']
        print('remaining balance:', cornichon.balanceOf(distributor).to('ether'))
    
    assert cornichon.balanceOf(distributor) == 0
