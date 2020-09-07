import click
import socket
import json
import os
import requests
import subprocess
import psutil

from cloud.mdb.clickhouse.tools.monrun_checks.result import Result


@click.command('resetup-state')
@click.option('-p', '--port', 'port', type=int, help='ClickHouse HTTP(S) port to use.')
@click.option('-s', '--ssl', 'ssl', is_flag=True, help='Use HTTPS rather than HTTP.')
@click.option('--ca_bundle', 'ca_bundle', help='Path to CA bundle to use.')
def resetup_state_command(port, ssl, ca_bundle):
    """
    Check state of resetup process.
    """

    check_resetup_runnning()
    check_resetup_required()

    host = socket.gethostname()
    if request(host, port, ssl, ca_bundle):
        return Result(2, 'ClickHouse listening on ports reserved for resetup')

    if os.path.isfile('/etc/clickhouse-server/config.d/resetup_config.xml'):
        return Result(2, 'Detected resetup config, but resetup is not running')

    return Result(0, 'OK')


def check_resetup_runnning():
    """
    Check for currently running ch-resetup
    """
    for proc in psutil.process_iter():
        if '/usr/bin/ch-resetup' in proc.name().lower():
            die(0, 'resetup running')


def check_resetup_required():
    """
    Check resetup conditions
    """
    cmd = ['sudo', 'salt-call', 'mdb_clickhouse.resetup_required', '--out', 'json', '--local']
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    if json.loads(output)['local']:
        die(0, 'OK')


def request(host, port, ssl, ca_bundle, query=None):
    """
    Send request to ClickHouse.
    """
    try:
        protocol = 'https' if ssl else 'http'
        verify = ca_bundle if ca_bundle else ssl
        params = {}
        if query:
            params['query'] = query

        r = requests.get(
            '{0}://{1}:{2}'.format(protocol, host, port),
            params=params,
            headers={
                'X-ClickHouse-User': 'mdb_monitor',
            },
            timeout=1,
            verify=verify)
        return r.status_code == 200 and r.text.strip() == 'Ok.'
    except Exception:
        die(0, 'OK')


def die(status, message):
    raise UserWarning(status, message)
