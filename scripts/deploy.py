import json
from brownie import MerkleDistributor, Cornichon, accounts, rpc, interface


def main():
    tree = json.load(open("snapshot/04-merkle.json"))
    user = accounts[0] if rpc.is_active() else accounts.load(input("account: "))
    root = tree["merkleRoot"]
    cornichon = Cornichon.deploy('Cornichon', 'CORN', tree['tokenTotal'], {'from': user})
    distributor = MerkleDistributor.deploy(cornichon, root, {"from": user})
    cornichon.transfer(distributor, cornichon.balanceOf(user))


def distribute():
    tree = json.load(open("snapshot/04-merkle.json"))
    whale = accounts.at('0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7', force=True)
    corn = Cornichon.deploy('Cornichon', 'CORN', tree['tokenTotal'], {'from': whale})
    dai = interface.ERC20('0x6B175474E89094C44Da98b954EedeAC495271d0F', owner=whale)
    distributor = MerkleDistributor.deploy(corn, tree["merkleRoot"], {"from": whale})
    corn.transfer(distributor, corn.balanceOf(whale))
    # claim from distributor
    for user, claim in tree['claims'].items():
        distributor.claim(claim['index'], user, claim['amount'], claim['proof'])
        assert corn.balanceOf(user) == claim['amount']
        print('remaining in distributor:', corn.balanceOf(distributor).to('ether'))
    assert corn.balanceOf(distributor) == 0
    # redeem dai
    dai.transfer(corn, corn.totalSupply())
    assert corn.rate() == '1 ether'
    for user in tree['claims']:
        user = accounts.at(user, force=True)
        corn.burn(corn.balanceOf(user), {'from': user})
        print('remaining supply:', corn.totalSupply().to('ether'))
        print('remaining dai:', dai.balanceOf(corn).to('ether'))
