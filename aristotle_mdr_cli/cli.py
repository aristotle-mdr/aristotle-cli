import click
import os


def get_subcommand(command):
    from importlib import import_module
    module = import_module("aristotle_mdr_cli.commands.%s" % command.lower())
    return getattr(module, 'command')


class Cli(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(os.path.join(os.path.dirname(__file__), 'commands')):
            if (
                filename.endswith('.py') and
                not filename.startswith('_') and
                not filename.startswith('.')
            ):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        return get_subcommand(name)


@click.command(cls=Cli)
def cli():
    """
    This collates all of the Aristotle Commands.
    """
    pass


if __name__ == "__main__":
    cli()
