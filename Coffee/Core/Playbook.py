# Copyright 2022 tkorays. All Rights Reserved.
# Licensed to MIT under a Contributor Agreement.
import abc
import os
import sys
import importlib


class Playbook(metaclass=abc.ABCMeta):
    """
    每个人都是艺术家，都能创造出可歌可泣的剧本。
    生活中的不如意让剧本来实现吧，按照你的想法。
    """
    @abc.abstractmethod
    def prepare(self):
        """
        舞台为你准备着，爱丽丝!
        """
        pass

    @abc.abstractmethod
    def play(self):
        """
        幕布拉开，故事开始。不妨背靠座椅，来一杯咖啡欣赏故事的流动。
        """
        pass


class PlaybookCommandLoader:
    """
    寻找一群可爱的人，去扮演剧本中的角色吧。
    """
    def __init__(self, click_group):
        self.click_group = click_group

    def load(self, module_name):
        m = importlib.import_module(module_name)
        m = importlib.reload(m)
        for c in m.commands:
            self.click_group.add_command(c)
        return self

    def load_multi(self, modules):
        for m in modules:
            self.load(m)

    def load_plays(self, playbook_module='Coffee.Playbook'):
        m = importlib.import_module(playbook_module)
        m = importlib.reload(m)
        mp = m.__dict__['__path__'][0]
        for f in os.listdir(mp):
            if f.startswith('__') or f.startswith('.') or not f.endswith('Playbook'):
                continue
            self.load(playbook_module + '.' + f)

    def load_custom_plays(self, path):
        sys.path.insert(0, path)
        for f in os.listdir(path):
            if f.startswith('__') or f.startswith('.') or not f.endswith('Playbook'):
                continue
            self.load(f)
