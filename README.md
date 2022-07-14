# defi-sdk

DeFi SDK is meant to handle ALL interactions with blockchain. It is structured to contain a module for each integrated protocol and a module for utilities needed accross different modules. As a principle, when creating an integration with a protocol, only functionalities that are needed at this time should be done. If only tracking data is needed, no transaction integrations are needed for example.

## Current integrations and requirements
- Aave v3
    - Data gathering
    - Transactions
- Uniswap v2
    - Data gathering
    - Transactions
- Staking (generalized frame for getting staked amount + accumulated rewards)
    - Quickswap LP staking

## Installing as package
```sh
pip install git+ssh://git@github.com/dkacapitalmgnt/defi-sdk.git
```
- Include 'abi' -folder in root of directory. This is used to save read ABIs or read ABIs from.
## Google secrets
- Add secrets to google cloud secret manager
- Create and download JSON key file to computer
- export GOOGLE_APPLICATION_CREDENTIALS="path-to-file" (no quotes)
- more information: https://cloud.google.com/secret-manager/docs/reference/libraries#create-service-account-console

## Updating
- Run setup with following commands:
```sh
git clone git@github.com:dkacapitalmgnt/defi-sdk.git
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install pip-tools
pip-compile requirements.in
pip install -r requirements.txt
```
- Include new requirements to requirements.in
- Include them to pyproject.toml as well under "dependencies"
- Compile requirements.txt using pip-compile requirements.in