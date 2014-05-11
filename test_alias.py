import unittest
import json
import io
import alias
from alias import Alias, Aliases, JSONBackend


class FakeAliasDatabase():
    def __init__(self):
        self.aliases = []

    def add_alias(self, alias):
        self.aliases.append(alias)

    def get_aliases(self):
        return self.aliases


def make_fake_aliases():
    return {'lst': Alias("lst", "ls -lhar --sort time"),
            'lss': Alias("lss", "ls -lhar --sort time")}


SIMPLE_ALIAS_JSON = """
{
    "aliases": {
        "lst" :{
            "command": "ls -lhar --sort time",
            "category": null
        }
    }
}
"""


def get_simple_alias_json_stringio():
    return io.StringIO(SIMPLE_ALIAS_JSON)


class TestAliasObj(unittest.TestCase):
    def test_comparisons(self):
        a1 = Alias('lst', 'ls -lhar --sort time')
        a2 = Alias('lst', 'ls -lhar --sort time')
        a3 = Alias('lss', 'ls -lhar --sort size')

        self.assertEqual(a1, a2)
        self.assertNotEqual(a1, a3)


class TestJSON(unittest.TestCase):
    def test_dicts_to_aliases(self):
        example = {
            "lst": {
                'command': 'ls -lhar --sort time',
                'category': None
            },
            "lss": {
                'command': 'ls -lhar --sort size',
                'category': None
            }
        }

        expected = {
            'lst': Alias('lst', 'ls -lhar --sort time'),
            'lss': Alias('lss', 'ls -lhar --sort size')
        }

        result = alias.dicts_to_aliases(example)

        self.assertDictEqual(result, expected)

    def test_decode(self):
        f = get_simple_alias_json_stringio()
        json.load(f, cls=alias.AliasesJSONDecoder)


def make_aliases(f=None):
    if f is None:
        f = io.StringIO()
    backend = JSONBackend(f)
    aliases = Aliases(backend)
    return aliases


class TestAlias(unittest.TestCase):
    def test_parse_alias(self):
        f = get_simple_alias_json_stringio()
        aliases = make_aliases(f)
        script = aliases.get_sh_script()
        self.assertEqual(script, 'alias lst="ls -lhar --sort time"\n')

    def test_add_alias(self):
        f = io.StringIO('{"aliases": {}}')
        aliases = make_aliases(f)

        aliases.add_alias(Alias("lst", "ls -lhar --sort time"))
        aliases.add_alias(Alias("lss", "ls -lhar --sort size"))
        script = aliases.get_sh_script()

        self.assertEqual('alias lss="ls -lhar --sort size"\n' +
                         'alias lst="ls -lhar --sort time"\n', script)

    def test_change_alias(self):
        f = io.StringIO('{"aliases": {}}')
        aliases = make_aliases(f)

        aliases.add_alias(Alias("lss", "ls -lhar --sort size"))
        aliases.add_alias(Alias("lss", "ls -lha --sort size"))

        script = aliases.get_sh_script()

        self.assertEqual('alias lss="ls -lha --sort size"\n', script)

    def test_backend(self):
        f = io.StringIO()
        backend = JSONBackend(f)
        backend.write_aliases(make_fake_aliases())

    def test_containsdoublequotes(self):
        aliases = make_aliases()

        aliases.add_alias(Alias('test', 'echo "This contains quotes"'))
        result = aliases.get_sh_script()

        expected = "alias test=\"echo \\\"This contains quotes\\\"\"\n"
        self.assertEqual(expected, result)

    def test_contains_brackets(self):
        aliases = make_aliases()

        aliases.add_alias(Alias('hasbrackets', 'echo (This is in brackets)'))
        result = aliases.get_sh_script()

        expected = 'alias hasbrackets="echo \\(This is in brackets\\)"\n'
        self.assertEqual(expected, result)
