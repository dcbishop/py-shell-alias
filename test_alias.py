import unittest
from alias import Aliases


class FakeAliasDatabase():
    def __init__(self):
        self.aliases = []

    def add_alias(self, alias, command):
        self.aliases.append((alias, command))

    def get_aliases(self):
        return self.aliases


class TestAlias(unittest.TestCase):
    def test_add_alias(self):
        alias_db = FakeAliasDatabase()
        alias = Aliases(alias_db)

        alias.add_alias("lst", "ls --lhar --sort time")
        script = alias.get_zsh_script()

        self.assertEqual('alias lst="ls --lhar --sort time"\n', script)
