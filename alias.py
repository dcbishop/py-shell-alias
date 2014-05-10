import json


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


def get_sh_alias_command(alias, command):
    return 'alias %s="%s"\n' % (alias, command)


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
        aliases = self.backend.get_aliases()

        alias_list = aliases_to_tuplelist(aliases)

        for alias in alias_list:
            new_line = get_sh_alias_command(alias[0], alias[1])
            script = script + new_line

        return script


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
            raise "WTF"
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

    def add_alias(self, alias):
        aliases = self.get_aliases()
        aliases[alias.alias] = alias
        self.write_aliases(aliases)
