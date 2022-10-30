import os
import sys
import signal
import tempfile

import click
import daemon
import pid
from pid import PidFile


PID_NAME = os.path.join(tempfile.gettempdir(), 'coffeed.pid')


def coffee_daemon():
    pid_file = PidFile(pidname=PID_NAME)

    with daemon.DaemonContext(stdout=sys.stdout,
                              stderr=sys.stderr,
                              stdin=sys.stdin,
                              pidfile=pid_file):
        print(f'coffee daemon started with pid file: {PID_NAME}')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Coffee.Service.settings')
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc
        execute_from_command_line(['manage.py', 'runserver'])


@click.group(help="cofd - coffee service!")
@click.version_option(package_name='pycoffee')
def coffeed():
    pass


@click.command('start', help='start coffee service')
def coffeed_start():
    try:
        coffee_daemon()
    except pid.PidFileAlreadyLockedError or pid.PidFileAlreadyRunningError:
        click.echo('coffee daemon already started!')


@click.command('stop', help='stop coffee service')
def coffeed_stop():
    try:
        with open(PID_NAME) as f:
            os.kill(int(f.readline()), signal.SIGKILL)
    except:
        print('Kill process failed! No pid or no process found!')


coffeed.add_command(coffeed_start)
coffeed.add_command(coffeed_stop)


if __name__ == "__main__":
    coffeed()