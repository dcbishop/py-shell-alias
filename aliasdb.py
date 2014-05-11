#!/usr/bin/env python
"""aliasdb.py.

Usage:
    aliasdb.py [--json=FILE] -s [-o OUTPUT]
    aliasdb.py -a <name> <command> [-j <aliases.json>]
    aliasdb.py <name>
    aliasdb.py (-h | --help)

Options:
    -s                          Generate shell script.
    -j FILE, --json=FILE        Read aliases from JSON file.
                                [default: ~/.config/aliases.json]
    -a <name> <command>         Add alias to database.
                                Will override any alias with the same name.
    -o OUTPUT, --output=OUTPUT  Output to file [default: -]
    -h --help                   Show help.
"""
__author__ = 'David C. Bishop'
__version__ = '1.0'
__license__ = 'CC0'

import json
import sys
import os
from pathlib import Path
from docopt import docopt


class Alias:
    """
    Represends a binding of a name to a command.
    """
    def __init__(self, alias_name, command, category=None):
        self.alias_name = alias_name
        self.command = command
        self.category = category
        if category == "":
            self.category = None

    def __eq__(self, other):
        if other is None:
            return -1
        if not isinstance(other, Alias):
            return -1
        return ((self.alias_name == other.alias_name) and
                (self.command == other.command) and
                (self.category == other.category))

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return str((self.alias_name, self.command, self.category))


def escape(string):
    """
    Escape quotes in a given string.
    """
    string = string.replace('"', '\\"')
    string = string.replace("'", "\\'")
    return string


def get_sh_alias_command(alias_name, command):
    """
    Output a line of sh script that makes a shell
    alias based on alias_name and command.
    """
    return 'alias %s="%s"\n' % (alias_name, escape(command))


def aliases_to_tuplelist(aliases):
    """
    Convert a dict containing aliases to a sorted list to tuples.
    """
    alias_list = []
    for key, value in aliases.items():
        alias_list.append((key, value.command))
    return sorted(alias_list)


class AliasDB:
    """
    Store and retrieve alias commands.
    """
    def __init__(self, backend):
        self.backend = backend

    def add_alias(self, alias):
        """
        Adds an Alias to the database.
        """
        self.backend.add_alias(alias)

    def get_sh_script(self):
        """
        Gets a sh script containing all the alias commands.
        """
        script = ""
        aliases = self.get_aliases()

        alias_list = aliases_to_tuplelist(aliases)

        for alias in alias_list:
            new_line = get_sh_alias_command(alias[0], alias[1])
            script = script + new_line

        return script

    def get_aliases(self):
        """
        Gets a dictionary containing all the aliases.
        """
        return self.backend.get_aliases()

    def get_alias(self, alias_name):
        """
        Gets a single alias based on it's name.
        """
        return self.get_aliases().get(alias_name, None)


class AliasesJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Alias):
            dobj = {
                'command': obj.command,
                'category': obj.category
            }
            return dobj
        return super(AliasesJSONEncoder, self).encode(obj)


def dict_to_alias(alias, item):
    """
    Convert a dict to an Alias object.
    """
    return Alias(alias, item['command'], item['category'])


def dicts_to_aliases(dlist):
    """
    Convert a dict of dicts to a dict of Alias objects.
    """
    olist = {}
    for item in dlist:
        alias = dict_to_alias(item, dlist[item])
        olist[item] = alias
    return olist


class AliasesJSONDecoder(json.JSONDecoder):
    def decode(self, json_string):
        if json_string == '':
            return {}
        default_obj = super(AliasesJSONDecoder, self).decode(json_string)
        if 'aliases' in default_obj:
            alias_objects = dicts_to_aliases(default_obj['aliases'])
            default_obj['aliases'] = alias_objects
        return default_obj


class JSONBackend:
    """
    A JSON Backend for AliasDB.
    """
    def __init__(self, fp):
        self.fp = fp

    def get_aliases(self):
        """
        Returns a dictionary of Aliases read from the file.
        """
        self.fp.seek(0)
        d = json.load(self.fp, cls=AliasesJSONDecoder)
        if 'aliases' in d:
            return d['aliases']
        return {}

    def write_aliases(self, aliases):
        """
        Writes out a dict of aliases to the file in JSON format.
        """
        self.fp.seek(0)
        json.dump({'aliases': aliases}, self.fp, cls=AliasesJSONEncoder,
                  indent=4, sort_keys=True)
        self.fp.truncate()

    def add_alias(self, alias):
        """
        Adds an alias to the JSON file.
        """
        aliases = self.get_aliases()
        aliases[alias.alias_name] = alias
        self.write_aliases(aliases)


def open_file(path):
    """
    Opens a file given by path. If the file doesn't exist try and create it.
    """
    if not path.exists():
        f = path.open('w')
        f.close()
    f = path.open('r+')
    return f


def make_aliasdb(path):
    """
    Makes an Aliases class with a JSON backend from the file given by path.
    """
    f = open_file(path)
    backend = JSONBackend(f)
    aliases = AliasDB(backend)
    return aliases


def process_opts(opts, aliases):
    """
    Takes a dictionary of options in the format output by docopt
    and talks to the alias database baned on them.
    """
    if opts['-a']:
        alias = Alias(opts['-a'], opts['<command>'])
        aliases.add_alias(alias)
    elif opts['-s']:
        script = aliases.get_sh_script()
        if opts['--output'] == "-":
            print(script)
        else:
            outpath = Path(opts['--output'])
            outfile = outpath.open('w')
            outfile.write(script)
            outfile.close()
    elif opts.get('<name>', None) is not None:
        alias = aliases.get_alias(opts['<name>'])
        if alias is not None:
            print(get_sh_alias_command(opts['<name>'], alias.command))


def main_opts(opts):
    """
    Run the program using the options given in opts which is expected
    to be a dictionary in the format output by docopt.
    """
    json_path = Path(os.path.expanduser(opts['--json']))
    aliases = make_aliasdb(json_path)
    process_opts(opts, aliases)


def main(args):
    """
    Run the program using the list of commandline arguments given in args.
    args[0] is expected to be the executable name.
    """
    opts = docopt(__doc__, args[1:])
    main_opts(opts)


if __name__ == "__main__":
    main(sys.argv)