import json
from brownie import Cornichon, MerkleDistributor, interface, accounts


def main():
    tree = json.load(open("snapshot/04-merkle.json"))
    whale = accounts.at("0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7", force=True)
    dai = interface.ERC20("0x6B175474E89094C44Da98b954EedeAC495271d0F", owner=whale)
    corn = Cornichon.at('0xa456b515303B2Ce344E9d2601f91270f8c2Fea5E', owner=whale)
    distributor = MerkleDistributor.at('0x8896C47Cf854644cDC4Dd949a11048a57bDBA9Bc', owner=whale)
    # a hacker sends everything back
    dai.transfer(corn, tree["tokenTotal"])

    for user, claim in tree["claims"].items():
        distributor.claim(claim["index"], user, claim["amount"], claim["proof"])
        assert corn.balanceOf(user) == claim["amount"]
        print("remaining in distributor:", corn.balanceOf(distributor).to("ether"))
    assert corn.balanceOf(distributor) == 0

    for user in tree["claims"]:
        user = accounts.at(user, force=True)
        amount = corn.balanceOf(user)
        before = dai.balanceOf(user)
        assert corn.rate() == "1 ether"
        corn.burn(amount, {"from": user})
        assert corn.balanceOf(user) == 0
        assert dai.balanceOf(user) == before + amount
        print("rate:", corn.rate().to("ether"))
        print("remaining supply:", corn.totalSupply().to("ether"))
        print("remaining dai:", dai.balanceOf(corn).to("ether"))

    assert dai.balanceOf(corn) == 0
    assert corn.totalSupply() == 0
