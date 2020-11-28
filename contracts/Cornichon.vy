# @version 0.2.7
from vyper.interfaces import ERC20

implements: ERC20

event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256

event Redeemed:
    receiver: indexed(address)
    corn: uint256
    dai: uint256


name: public(String[64])
symbol: public(String[32])
decimals: public(uint256)
balanceOf: public(HashMap[address, uint256])
allowances: HashMap[address, HashMap[address, uint256]]
initial_supply: uint256
total_supply: uint256
total_burned: public(uint256)
dai: ERC20


@external
def __init__(_name: String[64], _symbol: String[32], _supply: uint256):
    self.initial_supply = _supply
    self.name = _name
    self.symbol = _symbol
    self.decimals = 18
    self.dai = ERC20(0x6B175474E89094C44Da98b954EedeAC495271d0F)
    self.balanceOf[msg.sender] = _supply
    self.total_supply = _supply
    log Transfer(ZERO_ADDRESS, msg.sender, _supply)


@view
@external
def totalSupply() -> uint256:
    return self.total_supply


@view
@external
def allowance(_owner : address, _spender : address) -> uint256:
    return self.allowances[_owner][_spender]


@external
def transfer(_to : address, _value : uint256) -> bool:
    assert not _to in [self, ZERO_ADDRESS]
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    log Transfer(msg.sender, _to, _value)
    return True


@external
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    assert not _to in [self, ZERO_ADDRESS]
    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value
    self.allowances[_from][msg.sender] -= _value
    log Transfer(_from, _to, _value)
    return True


@external
def approve(_spender : address, _value : uint256) -> bool:
    self.allowances[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True


@view
@internal
def _rate(_corn: uint256) -> uint256:
    return _corn * (self.dai.balanceOf(self) + self.total_burned) / self.initial_supply


@view
@external
def rate() -> uint256:
    return self._rate(10 ** 18)


@internal
def _redeem(_to: address, _corn: uint256):
    _dai: uint256 = self._rate(_corn)
    self.total_burned += _corn
    self.dai.transfer(_to, _dai)
    log Redeemed(_to, _corn, _dai)


@internal
def _burn(_to: address, _value: uint256):
    assert _to != ZERO_ADDRESS
    self.total_supply -= _value
    self.balanceOf[_to] -= _value
    log Transfer(_to, ZERO_ADDRESS, _value)
    self._redeem(_to, _value)


@external
def burn(_value: uint256):
    self._burn(msg.sender, _value)


@external
def burnFrom(_to: address, _value: uint256):
    self.allowances[_to][msg.sender] -= _value
    self._burn(_to, _value)
