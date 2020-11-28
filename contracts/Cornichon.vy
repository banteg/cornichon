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

event Pickled:
    receiver: indexed(address)
    corn: uint256
    dai: uint256


name: public(String[64])
symbol: public(String[32])
decimals: public(uint256)
balanceOf: public(HashMap[address, uint256])
nonces: public(HashMap[address, uint256])
allowances: HashMap[address, HashMap[address, uint256]]
version: public(String[32])
total_supply: uint256
dai: ERC20
DOMAIN_SEPARATOR: public(bytes32)
DOMAIN_TYPE_HASH: constant(bytes32) = keccak256('EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)')
PERMIT_TYPE_HASH: constant(bytes32) = keccak256("Permit(address owner,address spender,uint256 amount,uint256 nonce,uint256 expiry)")


@external
def __init__(_name: String[64], _symbol: String[32], _supply: uint256):
    self.name = _name
    self.symbol = _symbol
    self.decimals = 18
    self.version = "1"
    self.dai = ERC20(0x6B175474E89094C44Da98b954EedeAC495271d0F)
    self.balanceOf[msg.sender] = _supply
    self.total_supply = _supply
    log Transfer(ZERO_ADDRESS, msg.sender, _supply)

    self.DOMAIN_SEPARATOR = keccak256(
        concat(
            DOMAIN_TYPE_HASH,
            keccak256(convert(self.name, Bytes[64])),
            keccak256(convert(self.version, Bytes[32])),
            convert(chain.id, bytes32),
            convert(self, bytes32)
        )
    )


@view
@external
def dom_sep() -> uint256:
    return chain.id


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
    if self.total_supply == 0:
        return 0
    return _corn * self.dai.balanceOf(self) / self.total_supply


@view
@external
def rate() -> uint256:
    return self._rate(10 ** 18)


@internal
def _redeem(_to: address, _corn: uint256):
    _dai: uint256 = self._rate(_corn)
    self.dai.transfer(_to, _dai)
    log Pickled(_to, _corn, _dai)


@internal
def _burn(_to: address, _value: uint256):
    assert _to != ZERO_ADDRESS
    self._redeem(_to, _value)
    self.total_supply -= _value
    self.balanceOf[_to] -= _value
    log Transfer(_to, ZERO_ADDRESS, _value)


@external
def burn(_value: uint256):
    self._burn(msg.sender, _value)


@external
def burnFrom(_to: address, _value: uint256):
    self.allowances[_to][msg.sender] -= _value
    self._burn(_to, _value)


@view
@internal
def message_digest(owner: address, spender: address, amount: uint256, nonce: uint256, expiry: uint256) -> bytes32:
    return keccak256(
        concat(
            b'\x19\x01',
            self.DOMAIN_SEPARATOR,
            keccak256(
                concat(
                    keccak256("Permit(address owner,address spender,uint256 amount,uint256 nonce,uint256 expiry)"),
                    convert(owner, bytes32),
                    convert(spender, bytes32),
                    convert(amount, bytes32),
                    convert(nonce, bytes32),
                    convert(expiry, bytes32),
                )
            )
        )
    )


@external
def permit(owner: address, spender: address, amount: uint256, nonce: uint256, expiry: uint256, signature: Bytes[65]) -> bool:
    assert expiry >= block.timestamp  # dev: permit expired
    assert owner != ZERO_ADDRESS  # dev: invalid owner
    assert nonce == self.nonces[owner]  # dev: invalid nonce
    digest: bytes32 = self.message_digest(owner, spender, amount, nonce, expiry)
    # NOTE: signature is packed as r, s, v
    r: uint256 = convert(slice(signature, 0, 32), uint256)
    s: uint256 = convert(slice(signature, 32, 32), uint256)
    v: uint256 = convert(slice(signature, 64, 1), uint256)
    assert ecrecover(digest, v, r, s) == owner  # dev: invalid signature

    self.allowances[owner][spender] = amount
    self.nonces[owner] += 1
    log Approval(owner, spender, amount)
    return True
