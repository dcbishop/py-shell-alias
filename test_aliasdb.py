import unittest
import io
import aliasdb
from aliasdb import Alias, AliasDB, JSONBackend


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


class TestAliasObj(unittest.TestCase):
    def test_comparisons(self):
        a1 = Alias('lst', 'ls -lhar --sort time')
        a2 = Alias('lst', 'ls -lhar --sort time')
        a3 = Alias('lss', 'ls -lhar --sort size')

        self.assertEqual(a1, a2)
        self.assertNotEqual(a1, a3)

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

        result = aliasdb.dicts_to_aliases(example)

        self.assertDictEqual(result, expected)


SIMPLE_ALIAS_YAML = """\
aliases:
    lst:
        command: "ls -lhar --sort time"
        category: null
"""


def make_simple_alias_yaml_stringio():
    return io.StringIO(SIMPLE_ALIAS_YAML)


def make_test_yaml_aliasdb(f=None):
    if f is None:
        f = io.StringIO()
    backend = aliasdb.YAMLBackend(f)
    adb = AliasDB(backend)
    return adb


class TestYAML(unittest.TestCase):
    def test_get_aliases(self):
        f = make_simple_alias_yaml_stringio()
        adb = make_test_yaml_aliasdb(f)

        result = adb.get_aliases()

        expected = {'lst': Alias('lst', 'ls -lhar --sort time')}
        self.assertEqual(expected, result)

    def test_write_aliases(self):
        f = make_simple_alias_yaml_stringio()
        adb = make_test_yaml_aliasdb(f)

        adb.add_alias(Alias('lss', 'ls -lhar --sort size'))
        result = f.getvalue()

        expected = """\
aliases:
    lss:
        category: null
        command: ls -lhar --sort size
    lst:
        category: null
        command: ls -lhar --sort time\n\
"""

        self.assertEqual(expected, result)

    def test_add_alias(self):
        adb = make_test_yaml_aliasdb()

        adb.add_alias(Alias("lst", "ls -lhar --sort time"))
        adb.add_alias(Alias("lss", "ls -lhar --sort size"))
        script = adb.get_sh_script()

        self.assertEqual('alias lss="ls -lhar --sort size"\n' +
                         'alias lst="ls -lhar --sort time"\n', script)


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


def make_simple_alias_json_stringio():
    return io.StringIO(SIMPLE_ALIAS_JSON)


def make_test_json_aliasdb(f=None):
    if f is None:
        f = io.StringIO()
    backend = JSONBackend(f)
    adb = AliasDB(backend)
    return adb


class TestJSON(unittest.TestCase):
    def test_parse_alias(self):
        f = make_simple_alias_json_stringio()
        adb = make_test_json_aliasdb(f)
        script = adb.get_sh_script()
        self.assertEqual(script, 'alias lst="ls -lhar --sort time"\n')

    def test_add_alias(self):
        adb = make_test_json_aliasdb()

        adb.add_alias(Alias("lst", "ls -lhar --sort time"))
        adb.add_alias(Alias("lss", "ls -lhar --sort size"))
        script = adb.get_sh_script()

        self.assertEqual('alias lss="ls -lhar --sort size"\n' +
                         'alias lst="ls -lhar --sort time"\n', script)

    def test_remove_alias(self):
        adb = make_test_json_aliasdb()
        adb.add_alias(Alias('one', 'one'))
        adb.add_alias(Alias('two', 'two'))
        adb.add_alias(Alias('three', 'three'))

        aliases = adb.get_aliases()
        self.assertEqual(len(aliases), 3)

        adb.remove_alias('two')
        aliases = adb.get_aliases()
        self.assertEqual(len(aliases), 2)

    def test_change_alias(self):
        adb = make_test_json_aliasdb()

        adb.add_alias(Alias("lss", "ls -lhar --sort size"))
        adb.add_alias(Alias("lss", "ls -lha --sort size"))

        script = adb.get_sh_script()

        self.assertEqual('alias lss="ls -lha --sort size"\n', script)


class TestScript(unittest.TestCase):
    def test_contains_singlequote(self):
        adb = make_test_json_aliasdb()

        adb.add_alias(Alias('test', "echo 'This contains quotes'"))
        result = adb.get_sh_script()

        expected = """alias test="echo \\\'This contains quotes\\\'"\n"""
        self.assertEqual(expected, result)

    def test_contains_doublequotes(self):
        adb = make_test_json_aliasdb()

        adb.add_alias(Alias('test', 'echo "This contains quotes"'))
        result = adb.get_sh_script()

        expected = "alias test=\"echo \\\"This contains quotes\\\"\"\n"
        self.assertEqual(expected, result)

    def test_contains_brackets(self):
        adb = make_test_json_aliasdb()

        adb.add_alias(Alias('hasbrackets', 'echo (This is in brackets)'))
        result = adb.get_sh_script()

        expected = 'alias hasbrackets="echo (This is in brackets)"\n'
        self.assertEqual(expected, result)
