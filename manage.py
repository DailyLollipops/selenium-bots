import botutilities
import click


@click.group()
def cli():
    pass
    

@click.command()
@click.argument('id')
@click.option('--name', '-n', default='', help='Bot name')
@click.option('--description', '-d', default='', help='Bot description')
def createbot(id, **kwargs):
    name = kwargs.pop('name')
    description = kwargs.pop('description')
    botutilities.createbot(id, name, description)


@click.command()
@click.argument('id')
@click.option('--params', '-p', default='{}', help='Bot params')
@click.option('--debug', '-d', is_flag=True, default=False, help='Enable verbose logging')
def runbot(id, **kwargs):
    params = kwargs.pop('params')
    debug = kwargs.pop('debug')
    botutilities.runbot(id, params, debug)

@click.command()
@click.argument('id')
def botinfo(id):
    botutilities.botinfo(id)

cli.add_command(createbot)
cli.add_command(runbot)
cli.add_command(botinfo)

if __name__ == '__main__':
    cli()
