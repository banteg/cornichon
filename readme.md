# Cornichon Snapshot

This repo contains everything to produce a snapshot of pre-hack DAI equivalent in pDAI Jar.

For a technical writeup of the hack, refer to [banteg/evil-jar](https://github.com/banteg/evil-jar) repo.

## Mainnet deployment

MerkleDistributor deployed at: [0x8896C47Cf854644cDC4Dd949a11048a57bDBA9Bc](https://etherscan.io/address/0x8896c47cf854644cdc4dd949a11048a57bdba9bc#code)

Cornichon deployed at: [0xa456b515303B2Ce344E9d2601f91270f8c2Fea5E](https://etherscan.io/address/0xa456b515303B2Ce344E9d2601f91270f8c2Fea5E#code)

## Deploy

To deploy the distributor on the mainnet:

```
brownie run snapshot deploy --network mainnet
```

## Claim

To claim the distribution:
```
brownie accounts import alias keystore.json
brownie run snapshot claim --network mainnet
```

## Tests

All testing is performed in a forked mainnet environment.

To run end to end claim and burn test:

```
brownie run distribution
```

To run the unit tests:

```
brownie test
```

## Validation

To generate the snapshot data:

```
pip install -r requirements.txt

brownie networks add Ethereum archive host=$YOUR_ARCHIVE_NODE chainid=1

rm -rf snapshot
brownie run snapshot --network archive
```
