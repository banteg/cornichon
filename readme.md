# Cornichon Snapshot

This repo contains everything to produce a snapshot of pre-hack DAI equivalent in pDAI Jar.

For a technical writeup of the hack, refer to [banteg/evil-jar](https://github.com/banteg/evil-jar) repo.

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
