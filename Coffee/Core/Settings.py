import configparser
import os


def as_ini(a_class):
    class Wrapper:
        def __init__(self, *args, **kwargs):
            self.__dict__['wrapped'] = a_class(*args, **kwargs)
            super(a_class, self.wrapped).__init__()
            self.wrapped.__dict__['__full_path__'] = ''
            self.__ini_vars__ = []
            for v in [v for v in a_class.__dict__ if not v.startswith('__') and not v.endswith('__')]:
                self.__ini_vars__.append(v)
                self.wrapped.__dict__[v] = a_class.__dict__[v]

        def __getattr__(self, item):
            return getattr(self.wrapped, item)

        def __setattr__(self, key, value):
            setattr(self.wrapped, key, value)

        def load(self, path):
            self.wrapped.__dict__['__full_path__'] = path
            if not os.path.exists(path):
                self.save(path)
            cfg = configparser.ConfigParser()
            cfg.read(path)
            for v in self.__ini_vars__:
                self.wrapped.__dict__[v] = type(a_class.__dict__[v])(cfg.get('main', v, fallback=a_class.__dict__[v]))
            return self

        def save(self, path=''):
            if not path and self.wrapped.__dict__['__full_path__']:
                path = self.wrapped.__dict__['__full_path__']
            cfg = configparser.ConfigParser()
            cfg.add_section('main')
            for v in self.__ini_vars__:
                cfg.set('main', v, str(self.wrapped.__dict__[v]))
            cfg.write(open(path, 'w'))

        def __str__(self):
            s = ''
            for v in self.__ini_vars__:
                s += f'{v}:{self.wrapped.__dict__[v]},'
            return s

        def __repr__(self):
            return self.__str__()

        def wrapped(self):
            return self.wrapped
    return Wrapper


@as_ini
class CoffeeSettings:
    version = '1.0'
    influxdb_host = '127.0.0.1'
    influxdb_port = 8086
    influxdb_username = ''
    influxdb_password = ''
    influxdb_database = 'coffee'
    grafana_url = '127.0.0.1:3000'
    grafana_key = ''
    local_user = ''
    storage_path = os.path.join(os.path.expanduser('~'), '.coffee')
    plays_path = os.path.join(os.path.expanduser('~'), '.coffee', 'CustomPlays')


DEF_CFG = CoffeeSettings().load(os.path.join(os.path.expanduser('~'), 'coffee.ini'))
