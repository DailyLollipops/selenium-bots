import importlib
import json
import re
import shutil

def createbot(id: str, name: str = '', description: str = ''):
    """
    Create a new bot

    :param id: Bot id
    :param name: Bot name
    :param description: Bot description 
    """
    template_path = 'bots/template'
    destination_path= f'bots/{id}'
    shutil.copytree(template_path, destination_path)
    with open(f'{destination_path}/handler.py', 'r+') as file:
        contents = file.read()
        contents = re.sub('from bots.template.botconfig', f'from bots.{id}.botconfig', contents)
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

def runbot(id, params: dict|str = {}, debug: bool = False):
    if isinstance(params, str):
        params = json.loads(params)
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

def botinfo(id):
    try:
        module = importlib.import_module(f'bots.{id}.botconfig')
        config = getattr(module, 'config')
    except ModuleNotFoundError:
        print('Invalid bot id')
        return
    except Exception as e:
        print(f'Error: {e}')
        return
    name = config.get('name', '')
    description = config.get('description', '')
    parameters = config.get('parameters', {})
    parameter_help_messages = []
    for key, value in parameters.items():
        parameter_help_format = f'{key}: {value.get('description', "")}'
        parameter_help_messages.append(parameter_help_format)

    msg_format = \
        f'''Bot ID: {id}
Bot name: {name}
Bot description: {description}
--------------------------------------
Parameters:
{"\n".join(parameter_help_messages)}
        '''
    print(msg_format)