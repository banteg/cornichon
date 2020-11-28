from brownie import Wei


def test_dai_amount(distributor, tree, cornichon):
    assert cornichon.balanceOf(distributor) == tree["tokenTotal"]


def test_tree_total(tree):
    claim_total = sum(v["amount"] for v in tree["claims"].values())

    assert claim_total == Wei(tree["tokenTotal"])
