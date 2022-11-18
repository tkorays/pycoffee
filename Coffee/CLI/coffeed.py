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
            from django.core.management import execute_from_command_line, ManagementUtility
        except ImportError as exc:
            raise ImportError("Couldn't import Django.") from exc
        ManagementUtility(['coffeed', 'runserver']).execute()


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
            print('stop success!')
    except:
        print('Kill process failed! No pid or no process found!')


@click.command('status', help='coffee service status')
def coffeed_status():
    try:
        with open(PID_NAME) as f:
            os.kill(int(f.readline()), signal.SIG_DFL)
            print('service is running')
    except OSError:
        print('service is not running')
    except:
        print('service is running')


coffeed.add_command(coffeed_start)
coffeed.add_command(coffeed_stop)
coffeed.add_command(coffeed_status)


if __name__ == "__main__":
    coffeed()
