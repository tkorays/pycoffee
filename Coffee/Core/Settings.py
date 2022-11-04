# Copyright 2022 tkorays. All Rights Reserved.
# Licensed to MIT under a Contributor Agreement.

import os
import yaml
from dataclasses import dataclass
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


DEF_SETTING_PATH = os.path.join(os.path.expanduser('~'), 'coffee.yaml')


@dataclass
class Setting(yaml.YAMLObject):
    version: str = '1.0'
    influxdb_host: str = '127.0.0.1'
    influxdb_port: int = 8086
    influxdb_username: str = ''
    influxdb_password: str = ''
    influxdb_database: str = 'coffee'
    grafana_url: str = '127.0.0.1:3000'
    grafana_key: str = ''
    grafana_influxdb_source: str = 'InfluxDB'
    local_user: str = ''
    storage_path: str = os.path.join(os.path.expanduser('~'), '.coffee')
    plays_path: str = os.path.join(os.path.expanduser('~'), '.coffee', 'CustomPlays')
    data_store_path: str = os.path.join(os.path.expanduser('~'), '.coffee', 'datastore')

    @staticmethod
    def load(path: str):
        with open(path, 'r') as f:
            return yaml.load(f, Loader=Loader)

    def save(self, path: str = ''):
        path = DEF_SETTING_PATH if not path else path
        with open(path, 'w') as f:
            yaml.dump(self, stream=f, Dumper=Dumper)

    def set(self, key: str, value: object):
        self.__setattr__(key, value)


DEF_CFG = Setting.load(DEF_SETTING_PATH)
