import click
import json
import requests
import os, sys
import textwrap
from socket import gaierror
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError

class Ping(object):
    def __init__(self, origin, user=None, password=None):
        self.registry = {
            'base': origin,
            'url': origin.rstrip('/')+'/api/v3',
            'username': user,
            'password': password,
        }

    def ping(self):
        return requests.get(
            self.registry['url']+'/about/',
        )

    def hello_are_you_there(self):
        return requests.get(
            self.registry['base'],
        )


@click.command()
@click.option('--registry', '-R', default='', help='Destination registry')
# @click.option('--user', default=None, help='API username')
# @click.option('--password', default=None, help='API password')
def command(registry):
    """
    Get info about a registry.
    """
    # r = send_request(manifest, api, user, password)
    # print(r.status_code, r.text)

    try:
        r = Ping(registry).ping()
    except requests.exceptions.RequestException as e:
        click.echo("Something went terribly wrong, is that even a valid url?")
        return(sys.exit)

    if r.status_code == 404:
        failsafe = Ping(registry).hello_are_you_there()
        if failsafe.status_code == 200:
            click.echo("\n".join([
                "The requested site seems to be there, but:",
                "\t* the Aristotle API is running a version lower than version 3",
                "\t* the Aristotle API isn't installed",
                "\t* or it isn't an Aristotle Metadata Registry",
            ]))
        else:
            click.echo("The given address is not accessible")
        return(sys.exit)

    data = r.json()
    click.echo(
        textwrap.dedent("""
        {name}
        {line}
        
        Aristotle Metadata Registry v{version}
        
        Description: {description}
        
        Extra information
        -----------------
        {capabilities}
        """).format(
            name=data['name'],
            version=data['aristotle_mdr']['version'],
            line="="*len(data['name']),
            description=data['description'],
            capabilities=r.text,
        )
    )


if __name__ == "__main__":
    command()
