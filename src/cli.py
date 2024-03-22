#!/usr/bin/env python
import getpass
import pickle
import click
import difflib
import subprocess
import io
import paramiko
from pyonepassword.api.exceptions import OPNotFoundException
from src.ssh import open_shell
from src.onepassword import onepasswordtool

@click.group()
@click.pass_context
def cli(ctx):
    try:
        ctx.obj = pickle.load(open("/tmp/opt.pickle", "rb"))
    except FileNotFoundError:
        ctx.obj = onepasswordtool()
        with open("/tmp/opt.pickle", "wb") as f:
            pickle.dump(ctx.obj, f)
    except AttributeError:
        ctx.obj = onepasswordtool()
        with open("/tmp/opt.pickle", "wb") as f:
            pickle.dump(ctx.obj, f)
    pass

@cli.command()
@click.argument("item")
@click.pass_obj
def get_password(ctx, item):
    try:
        item_password = ctx.get_item(item)
        click.echo(item_password)
    except OPNotFoundException as e:
        click.echo(e)

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
            vault = ctx.match_vault(vault)
        item = ctx.match_item(pem_file)
        pem_name, pem_bytes = ctx.op.document_get(item, vault=vault)
        pem_bytes = pem_bytes.decode("utf-8")
        ssh = paramiko.SSHClient()
        pem_bytes = io.StringIO(pem_bytes)
        ssh_key = paramiko.RSAKey.from_private_key(pem_bytes, password=password)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, pkey=ssh_key)
        open_shell(ssh)
    except OPNotFoundException as e:
        click.echo(e)

#@cli.command()
#@click.argument("data", type=str, nargs=-1)
#@click.pass_obj
#def generate_secret(ctx, data):
#    data = [item.split("|") for item in data]
#    for tup in data:
#        try:
#            result = ctx.get_item(tup[1])
#            if result is None:
#                raise OPNotFoundException
#            tup[1] = result
#        except OPNotFoundException:
#            click.echo(f"Could not find item {tup[1]} or duplicates, try specifiying the vault")
#            exit(-1)
#        except IndexError:
#            click.echo("Invalid 1Password target, did you add the target field?")
#    yaml = secret.generate_yaml(data)
#    click.echo(yaml)

@cli.command()
@click.argument("template")
@click.pass_obj
def print_template(ctx, template):
    output = ctx.render_secret(template)
    click.echo(output)

@cli.command()
@click.argument("template")
@click.argument("secret_name")
@click.option("--pubkey", '-p', default="pub-sealed-secrets.pem")
@click.pass_obj
def create_secret(ctx, template, secret_name, pubkey):
    cmd_str = f"kubectl create secret generic test --dry-run=client --from-file={secret_name}=<(1password-tool print-template {template}) -o yaml | kubeseal --cert {pubkey} > {secret_name}-sealed.yaml"
    x = subprocess.run(cmd_str, shell=True, check=True, text=True)
    click.echo(x)

@cli.command()
@click.pass_obj
def list_vaults(ctx):
    ctx.get_vaults()
    for vault in ctx.vaults:
        click.echo(vault) 

@cli.command()
@click.pass_obj
def list_items(ctx):
    ctx.get_items()
    for item in ctx.items:
        click.echo(item)

if __name__ == "__main__":
    cli()
