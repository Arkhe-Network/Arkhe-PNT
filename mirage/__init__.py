class Workspace:
    def __init__(self, mounts):
        self._mounts = mounts
        self._commands = {}

    def command(self, name, handler):
        self._commands[name] = handler

    async def execute(self, cmd):
        # mock execution
        if 'rm -rf' in cmd:
            raise Exception("Cannot remove root")
        return f"Executed {cmd} successfully"
