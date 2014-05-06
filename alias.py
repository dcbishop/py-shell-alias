class Aliases:
    def __init__(self, backend):
        self.backend = backend

    def add_alias(self, alias, command):
        self.backend.add_alias(alias, command)

    def get_zsh_script(self):
        script = ""
        aliases = self.backend.get_aliases()

        for alias in aliases:
            script = script + 'alias ' + alias[0] + '="' + alias[1] + '"\n'

        return script
