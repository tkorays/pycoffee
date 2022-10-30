# Copyright 2022 tkorays. All Rights Reserved.
# Licensed to MIT under a Contributor Agreement.

import os
import sys
import click
import shutil

# add base directory to the search path if run this script directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


from Coffee.Core.Settings import DEF_CFG
from Coffee.Core.Playbook import PlaybookCommandLoader


CWD = os.path.split(os.path.realpath(__file__))[0]


@click.group(help="Coffee - coffee time!")
@click.version_option(package_name='pycoffee')
def coffee():
    pass


@click.group('play', help='[in] custom playbooks')
def coffee_play():
    pass


@click.command("config", help="[in] config the coffee")
@click.option('--influxdb_host', type=str, default='', required=False, help="InfluxDB service host")
@click.option('--influxdb_port', type=str, default='', required=False, help="InfluxDB service port")
@click.option('--influxdb_username', type=str, default='', required=False, help='username of InfluxDB')
@click.option('--influxdb_password', type=str, default='', required=False, help='password of InfluxDB')
@click.option('--influxdb_database', type=str, default='', required=False, help='InfluxDB database name')
@click.option('--local_user', type=str, default='', required=False, help='user name')
@click.option('--grafana_url', type=str, default='', required=False, help='grafana url')
@click.option('--grafana_key', type=str, default='', required=False, help='grafana api key')
@click.option('--grafana_influxdb_source', type=str, default='', required=False, help='grafana influxdb source name')
def coffee_config(influxdb_host, influxdb_port, influxdb_username, influxdb_password, influxdb_database,
                  local_user, grafana_url, grafana_key, grafana_influxdb_source):
    cfg_modified = False
    if influxdb_host:
        DEF_CFG.influxdb_host = influxdb_host
        cfg_modified = True
    if influxdb_port:
        DEF_CFG.influxdb_port = influxdb_port
        cfg_modified = True
    if influxdb_username:
        DEF_CFG.influxdb_username = influxdb_username
        cfg_modified = True
    if influxdb_password:
        DEF_CFG.influxdb_password = influxdb_password
        cfg_modified = True
    if influxdb_database:
        DEF_CFG.influxdb_database = influxdb_database
        cfg_modified = True
    if local_user:
        DEF_CFG.local_name = local_user
        cfg_modified = True
    if grafana_url:
        DEF_CFG.grafana_url = grafana_url
        cfg_modified = True
    if grafana_key:
        DEF_CFG.grafana_key = grafana_key
        cfg_modified = True
    if grafana_influxdb_source:
        DEF_CFG.grafana_influxdb_source = grafana_influxdb_source
        cfg_modified = True

    if cfg_modified:
        DEF_CFG.save()


@click.command('play-add', help='[in] add custom play')
@click.option('--name', default='', required=True, help='name of this play')
@click.option('--source', default='', required=True, help='repo source name')
@click.option('--git-prefix', default='', required=False, help='add from git repo')
def coffee_add_play(name, source, git_prefix):
    if not name or not source:
        click.echo('name and source should be specified!')
        return
    if not git_prefix:
        git_prefix = 'https://github.com/'

    if not name.endswith('Playbook'):
        click.echo("playbook's name should end with `Playbook`! Please modify name and try again.")
        return

    if os.path.exists(os.path.join(DEF_CFG.plays_path, name)):
        click.echo(f'{name} has already been added, we will not add it again.')
        return

    if 0 == os.system(f'git clone {git_prefix}/{source} {os.path.join(DEF_CFG.plays_path, name)}'):
        click.echo('add success')
    else:
        click.echo("failed to add play")


@click.command('play-remove', help='[in] add custom play')
@click.option('--name', default='', required=True, help='name of this play')
def coffee_remove_play(name):
    if not click.confirm('sure to remove this play?'):
        click.echo(f'playbook {name} is not removed!')
        return
    shutil.rmtree(os.path.join(DEF_CFG.plays_path, name), ignore_errors=True)


@click.command('play-update', help='[in] add custom play')
@click.option('--name', default='', required=True, help='name of this play')
def coffee_update_play(name):
    if not os.path.exists(os.path.join(DEF_CFG.plays_path, name)):
        click.echo('playbook not exists!')
        return
    if not os.path.exists(os.path.join(DEF_CFG.plays_path, name, '.git')):
        click.echo('not a git repo, can not update')
        return
    if 0 == os.system(f"cd {os.path.join(DEF_CFG.plays_path, name)} && git pull origin master"):
        click.echo('update success')
    else:
        click.echo("update filed!")


@click.command('play-new', help='[in] create a play')
@click.option('--name', default='', required=True, help='name of this play')
def coffee_new_play(name):
    play_dir = os.path.join(DEF_CFG.plays_path, name)
    if 0 == os.system(f'mkdir {play_dir} && cd {play_dir} && git init . && touch __init__.py'):
        click.echo('create play success!')
    else:
        click.echo('create play failed')


coffee.add_command(coffee_play)
coffee.add_command(coffee_config)
coffee.add_command(coffee_add_play)
coffee.add_command(coffee_remove_play)
coffee.add_command(coffee_update_play)
coffee.add_command(coffee_new_play)

if not os.path.exists(DEF_CFG.storage_path):
    os.mkdir(DEF_CFG.storage_path)
if not os.path.exists(DEF_CFG.plays_path):
    os.mkdir(DEF_CFG.plays_path)
if not os.path.exists(DEF_CFG.data_store_path):
    os.mkdir(DEF_CFG.data_store_path)

# load internal playbooks
PlaybookCommandLoader(coffee).load_multi([
    'Coffee.Playbook.PowerToys'
])
# load local playbooks for debug
PlaybookCommandLoader(coffee_play).load_custom_plays(
    os.path.join(CWD, '../../CoffeePlaybooks')
)
# load custom playbooks
PlaybookCommandLoader(coffee_play).load_custom_plays(DEF_CFG.plays_path)


# run this script directly.
if __name__ == "__main__":
    coffee()
