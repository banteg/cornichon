import json
import click
from brownie import MerkleDistributor, Cornichon, Wei, accounts, interface, rpc


CORNICHON = "0xa456b515303B2Ce344E9d2601f91270f8c2Fea5E"
DISTRIBUTOR = "0x8896C47Cf854644cDC4Dd949a11048a57bDBA9Bc"


def get_user():
    if rpc.is_active():
        return accounts.at("0x751B640E0AbE005548286B5e15353Edc996DE1cb", force=True)
    else:
        print("Available accounts:", accounts.load())
        return accounts.load(input("account: "))


def main():
    tree = json.load(open("snapshot/04-merkle.json"))
    user = get_user()
    dist = MerkleDistributor.at(DISTRIBUTOR, owner=user)
    corn = Cornichon.at(CORNICHON, owner=user)
    if user not in tree["claims"]:
        return click.secho(f"{user} is not included in the distribution", fg="red")
    claim = tree["claims"][user]
    if dist.isClaimed(claim["index"]):
        return click.secho(f"{user} has already claimed", fg="yellow")

    amount = Wei(int(claim["amount"], 16)).to("ether")
    _amount = click.style(f"{amount:,.2f} CORN", fg="green", bold=True)
    print(f"Claimable amount: {_amount}")
    dist.claim(claim["index"], user, claim["amount"], claim["proof"])


def burn():
    user = get_user()
    corn = Cornichon.at(CORNICHON, owner=user)
    balance = corn.balanceOf(user).to("ether")
    rate = corn.rate().to("ether")
    _corn = click.style(f"{balance:,.2f} CORN", fg="green", bold=True)
    _dai = click.style(f"{balance * rate:,.2f} DAI", fg="green", bold=True)
    _rate = click.style(f"{rate:,.5%}", fg="green", bold=True)
    _burn = click.style("burn", fg="red", bold=True)
    print(f"You have {_corn}, which can be burned for {_dai} at a rate of {_rate}")
    if click.confirm(f"Do you want to {_burn} CORN for DAI?"):
        corn.burn()
