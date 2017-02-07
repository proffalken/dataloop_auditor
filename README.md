# Dataloop Check List

Documents your agents in Dataloop and the checks associated with them and dumps
them all out in a number of formats

## Using Dataloop Check List

Create a virtual environment

`mkvirtualenv dlchecks`

Install the requirements

`pip install -r requirements.txt`

Copy `config.yml.sample` to `config.yml` and update it with your API key, organisation name and the accounts that you want to analyse

Run the script `./dlchecks.py > dataloop.md`

Upload the results to your git repository or other Markdown compatible
documentation location
