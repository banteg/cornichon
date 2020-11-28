# @version 0.2.7
interface Token:
    def balanceOf(user: address) -> uint256: view
    def burnFrom(user: address, amount: uint256): nonpayable
    def transfer(user: address, amount: uint256) -> bool: nonpayable

indicator: Token
token: Token


@external
def __init__(_indicator: address, _token: address):
    self.indicator = Token(_indicator)
    self.token = Token(_token)


@external
def redeem(_amount: uint256 = MAX_UINT256):
    amount: uint256 = _amount
    if amount == MAX_UINT256:
        amount = min(self.indicator.balanceOf(msg.sender), self.token.balanceOf(self))
    self.indicator.burnFrom(msg.sender, amount)
    self.token.transfer(msg.sender, amount)
