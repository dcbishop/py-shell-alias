#!/usr/bin/env python
"""alias.py.

Usage:
    alias.py [--json=FILE] -s [-o OUTPUT]
    alias.py -a <name> <command> [-j <aliases.json>]
    alias.py <name>
    alias.py (-h | --help)

Options:
    -s                          Generate shell script.
    -j FILE, --json=FILE        Read aliases from JSON file.
                                [default: ~/.config/aliases.json]
    -a <name> <command>         Add alias to database.
                                Will override any alias with the same name.
    -o OUTPUT, --output=OUTPUT  Output to file [default: -]
    -h --help                   Show help.
"""
import json
import sys
import os
from pathlib import Path
from docopt import docopt


class Alias:
    def __init__(self, alias, command, category=None):
        self.alias = alias
        self.command = command
        self.category = category
        if category == "":
            self.category = None

    def __eq__(self, other):
        if other is None:
            return -1
        if not isinstance(other, Alias):
            return -1
        return ((self.alias == other.alias) and
                (self.command == other.command) and
                (self.category == other.category))

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return str((self.alias, self.command, self.category))


def escape(string):
    string = string.replace('"', '\\"')
    string = string.replace("'", "\\'")
    return string


def get_sh_alias_command(alias, command):
    return 'alias %s="%s"\n' % (alias, escape(command))


def aliases_to_tuplelist(aliases):
    """
    Convert a dict containing aliases to a sorted list to tuples.
    """
    alias_list = []
    for key, value in aliases.items():
        alias_list.append((key, value.command))
    return sorted(alias_list)


class Aliases:
    def __init__(self, backend):
        self.backend = backend

    def add_alias(self, alias):
        self.backend.add_alias(alias)

    def get_sh_script(self):
        script = ""
        aliases = self.get_aliases()

        alias_list = aliases_to_tuplelist(aliases)

        for alias in alias_list:
            new_line = get_sh_alias_command(alias[0], alias[1])
            script = script + new_line

        return script

    def get_aliases(self):
        return self.backend.get_aliases()

    def get_alias(self, aliasname):
        return self.get_aliases().get(aliasname, None)


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
    def __init__(self, fp):
        self.fp = fp

    def get_aliases(self):
        self.fp.seek(0)
        d = json.load(self.fp, cls=AliasesJSONDecoder)
        if 'aliases' in d:
            return d['aliases']
        return {}

    def write_aliases(self, aliases):
        self.fp.seek(0)
        json.dump({'aliases': aliases}, self.fp, cls=AliasesJSONEncoder,
                  indent=4, sort_keys=True)
        self.fp.truncate()

    def add_alias(self, alias):
        aliases = self.get_aliases()
        aliases[alias.alias] = alias
        self.write_aliases(aliases)


def open_file(path):
    if not path.exists():
        f = path.open('w')
        f.close()
    f = path.open('r+')
    return f


def make_aliasdb(path):
    f = open_file(path)
    backend = JSONBackend(f)
    aliases = Aliases(backend)
    return aliases


def process_opts(opts, aliases):
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
    json_path = Path(os.path.expanduser(opts['--json']))
    aliases = make_aliasdb(json_path)
    process_opts(opts, aliases)


def main(args):
    opts = docopt(__doc__, args[1:])
    main_opts(opts)


if __name__ == "__main__":
    main(sys.argv)
