import click
import json
import requests
import os, sys
import textwrap
from socket import gaierror
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError

from aristotle_mdr_cli import utils

class CheckCreds(utils.AristotleCommand):
    def __init__(self, origin, user=None, password=None):
        self.registry = {
            'base': origin,
            'url': origin.rstrip('/')+'/api/v2',
            'username': user,
            'password': password,
        }

    def credentials(self):
        return requests.get(
            self.registry['url']+'/',
            auth=(self.registry['username'], self.registry['password']),
        )


@click.command()
@click.option('--registry', '-R', default='', help='Destination registry')
@click.option('--user', prompt=True, help='API username')
@click.option('--password', prompt=True, hide_input=True, default=None, help='API password')
def command(registry, user, password):
    """
    Check if credentials are valid for a registry.
    """

    try:
        r = CheckCreds(registry, user, password).credentials()
    except requests.exceptions.RequestException as e:
        click.echo("Something went terribly wrong, is that even a valid url?")
        return(sys.exit)

    if r.status_code == 404:
        failsafe = Ping(registry).hello_are_you_there()
        if failsafe.status_code == 200:
            click.echo("\n".join([
                "The requested site seems to be there, but:",
                "\t* the Aristotle API is running a version lower than version 2.1",
                "\t* the Aristotle API isn't installed",
                "\t* or it isn't an Aristotle Metadata Registry",
            ]))
        else:
            click.echo("The given address is not accessible")
        return(sys.exit)

    if r.status_code == 403:
        click.echo("Credentials are bad - 403")
    elif r.status_code == 200:
        click.echo("Credentials are good - 200")
    else:
        click.echo("Something went wrong - {}".format(r.status_code))


if __name__ == "__main__":
    command()
