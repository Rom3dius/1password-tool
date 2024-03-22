#!/usr/bin/env python
import getpass
import click
import difflib
import io
from pyonepassword import OP
from pyonepassword.api.exceptions import (
    OPSigninException,
    OPItemGetException,
    OPNotFoundException,
    OPConfigNotFoundException
)
from ssh import open_shell
import paramiko

@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = do_signin()
    pass

@cli.command()
@click.argument("vault")
@click.argument("item")
@click.pass_obj
def get_password(ctx, vault, item):
    try:
        vault = match_vault(vault, ctx.vault_list())
        item = match_item(item, ctx.item_list(vault=vault))
        item_password = ctx.item_get_password(item, vault=vault)
        click.echo(item_password)
    except OPNotFoundException as e:
        click.echo("Item not found")
        click.echo(e)
    except OPItemGetException as e:
        click.echo("Unable to retrieve item")
        click.echo(e)
    except IndexError:
        click.echo("Item not found")

@cli.command()
@click.argument("host")
@click.argument("pem-file")
@click.option("--vault", default=None)
@click.option("--password", default=None)
@click.pass_obj
def ssh(ctx, host, pem_file, vault, password):
    try:
        username = host.split("@")[0]
        host = host.split("@")[1]
        if vault is not None:
            vault = match_vault(vault, ctx.vault_list())
        item = match_item(pem_file, ctx.item_list(vault=vault))
        pem_name, pem_bytes = ctx.document_get(item, vault=vault)
        pem_bytes = pem_bytes.decode("utf-8")
        ssh = paramiko.SSHClient()
        pem_bytes = io.StringIO(pem_bytes)
        ssh_key = paramiko.RSAKey.from_private_key(pem_bytes, password=password)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, pkey=ssh_key)
        open_shell(ssh)
    except IndexError:
        click.echo("Item not found")

@cli.command()
@click.argument("vault")
@click.argument("file")
@click.pass_obj
def get_file(ctx, vault, file):
    try:
        vault = match_vault(vault, ctx.vault_list())
        file = match_item(file, ctx.item_list(vault=vault))
        file_name, document_bytes = ctx.document_get(file, vault=vault)
        click.echo(file)
    except OPNotFoundException as e:
        click.echo("Item not found")
        click.echo(e)
    except OPItemGetException as e:
        click.echo("Unable to retrieve item")
        click.echo(e)
    except IndexError:
        click.echo("Item not found")

@cli.command()
@click.pass_obj
def list_vaults(ctx):
    vaults = ctx.vault_list()
    for vault in vaults:
        click.echo(vault['name'])

if __name__ == "__main__":
    cli()
