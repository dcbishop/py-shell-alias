aliasdb.py
----------

Keeps a persistent list of alias command for the shell in either YAML or JSON format.

Requires Python 3, docopt and pyyaml:
    % python -m ensurepip --upgrade
    % pip3 install docopt yaml

To add an alias (to the default database in ~/.config/aliases.yaml):

    % ./aliasdb.py -a lst "ls -lhr --sort size"

To print out all aliases as a sh script:

    % ./aliasdb.py -s
    alias lss="ls -lhr --sort size"
    alias lst="ls -lhr --sort time"

Remove an alias with:

    % ./aliasdb.py -r lst

Specify a json file:

    % ./aliasdb.py --json=aliases.json -a lst "ls -lhr --sort size"

To write out a shell script with aliases loaded from a YAML file to a specified file:

    % ./aliasdb.py --yaml=aliases.yaml -s --output=aliases.sh

For help:

    % ./aliasdb.py --help

Run test suite:

    % python -m unittest
