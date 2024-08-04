import click
import importlib
import re
import shutil
import textwrap

@click.group()
def cli():
    pass

createbot_help = textwrap.dedent(
'''
Create a new bot.

Required:\n
- id: Bot id name\n
Optional:\n
- name (--name, -n): Bot name\n
- description (--description, -d): Bot description\n
'''
)
@click.command(help=createbot_help)
@click.argument('id')
@click.option('--name', '-n', help='Bot name')
@click.option('--description', '-d', help='Bot description')
def createbot(id, **kwargs):
    """
    Create a new bot
    """
    template_path = 'bots/template'
    destination_path= f'bots/{id}'
    shutil.copytree(template_path, destination_path)
    name = kwargs.pop("name")
    description = kwargs.pop("description")
    with open(f'{destination_path}/handler.py', 'r+') as file:
        contents = file.read()
        contents = re.sub('from botconfig', f'from bots.{id}.botconfig', contents)
        file.seek(0)
        file.truncate()
        file.write(contents)
    with open(f'{destination_path}/botconfig.py', 'r+') as file:
        contents = file.read()
        contents = re.sub(f'"id": ""', f'"id": "{id}"', contents)
        if name:
            contents = re.sub(f'"name": ""', f'"name": "{name}"', contents)
        if description:
            contents = re.sub(f'"description": ""', f'"name": "{description}"', contents)
        file.seek(0)
        file.truncate()
        file.write(contents)

runbot_help = textwrap.dedent(
'''
Run a bot.

Required:\n
- id: Bot id name\n
Optional:\n
- params (--params, -p): Bot params
- debug (--debug, -d): Enable verbose logging
'''
)
@click.command(help=runbot_help)
@click.argument('id')
@click.option('--params', '-p', help='Bot params')
@click.option('--debug', '-d', is_flag=True, default=False, help='Enable verbose logging')
def runbot(id, **kwargs):
    params = kwargs.get('params', {})
    debug = kwargs.get('debug', False)
    try:
        module = importlib.import_module(f'bots.{id}.handler')
        handler = getattr(module, 'BotHandler')
    except ModuleNotFoundError:
        print('Invalid bot id')
        return
    except Exception as e:
        print(f'Error: {e}')
        return
    bot = handler(params=params, debug=debug)
    bot.handle()

cli.add_command(createbot)
cli.add_command(runbot)

if __name__ == '__main__':
    cli()
