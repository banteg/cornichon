from eth_account.messages import encode_structured_data
from brownie import chain
from eth_account import Account
from eth_utils import encode_hex
from eth_account._utils.structured_data.hashing import hash_domain


def test_permit(cornichon):
    owner = Account.create()
    spender = Account.create()
    nonce = cornichon.nonces(owner.address)
    expiry = chain[-1].timestamp + 3600
    amount = 10 ** 21
    data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "Permit": [
                {"name": "owner", "type": "address"},
                {"name": "spender", "type": "address"},
                {"name": "amount", "type": "uint256"},
                {"name": "nonce", "type": "uint256"},
                {"name": "expiry", "type": "uint256"},
            ],
        },
        "domain": {
            "name": cornichon.name(),
            "version": cornichon.version(),
            "chainId": 1,
            "verifyingContract": str(cornichon),
        },
        "primaryType": "Permit",
        "message": {
            "owner": owner.address,
            "spender": spender.address,
            "amount": amount,
            "nonce": nonce,
            "expiry": expiry,
        },
    }
    message = encode_structured_data(data)
    signed = owner.sign_message(message)
    assert encode_hex(hash_domain(data)) == cornichon.DOMAIN_SEPARATOR()
    tx = cornichon.permit(
        owner.address, spender.address, amount, nonce, expiry, signed.signature
    )
    assert cornichon.allowance(owner.address, spender.address) == amount
