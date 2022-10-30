

class Plugin:
    def __init__(self):
        self.plays = []
        self.cmd_group = None

    def get_plays(self):
        return self.plays

    def get_cmd_group(self):
        return self.cmd_group
