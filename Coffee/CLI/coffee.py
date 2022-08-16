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
@click.option('--git-url', default='', required=False, help='add from git repo')
def coffee_add_play(name, git_url):
    if not git_url:
        click.echo('arguments error!')
        return
    if 0 == os.system(f'git clone {git_url} {os.path.join(DEF_CFG.plays_path, name)}'):
        click.echo('add success')
    else:
        click.echo("failed to add play")


@click.command('play-remove', help='[in] add custom play')
@click.option('--name', default='', required=True, help='name of this play')
def coffee_remove_play(name):
    shutil.rmtree(os.path.join(DEF_CFG.plays_path, name), ignore_errors=True)


coffee.add_command(coffee_play)
coffee.add_command(coffee_config)
coffee.add_command(coffee_add_play)
coffee.add_command(coffee_remove_play)

if not os.path.exists(DEF_CFG.storage_path):
    os.mkdir(DEF_CFG.storage_path)
if not os.path.exists(DEF_CFG.plays_path):
    os.mkdir(DEF_CFG.plays_path)

PlaybookCommandLoader(coffee).load_multi([
    'Coffee.Playbook.PowerToys'
])
PlaybookCommandLoader(coffee_play).load_custom_plays(DEF_CFG.plays_path)


# run this script directly.
if __name__ == "__main__":
    coffee()
