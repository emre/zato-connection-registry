import click

from .registry import Registry


@click.group()
def cli():
    pass


@cli.command()
@click.argument('address')
@click.argument('credentials')
@click.argument('to_file')
def backup(address, credentials, to_file):
    username, password = credentials.split(":")
    registry = Registry(
        address,
        username,
        password,
    )
    registry.dump_to_json(to_file)
    print("Backup completed. See %s." % to_file)


@cli.command()
@click.argument('address')
@click.argument('credentials')
@click.argument('from_file')
def restore(address, credentials, from_file):
    username, password = credentials.split(":")
    restore_registry = Registry(
        address,
        username,
        password,
    )
    restore_registry.restore_rest_channels(from_file=from_file)
    print("Restore completed. See %s" % from_file)
