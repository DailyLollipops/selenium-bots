from bots.template.botconfig import config
from seleniumbot.enums import Driver
from bots.common.basehandler import BaseHandler

import click
import json

class BotHandler(BaseHandler):
    def __init__(self, params: dict = {}, debug: bool = False) -> None:
        super().__init__(Driver.CHROME, config=config, params=params, debug=debug)
        
    def run(self):
        """
        Bot entry point function.
        """
        pass


if __name__ == '__main__':
    @click.command()
    @click.option('--params', '-p', default='{}', help='Bot handler parameters')
    @click.option('--debug', '-d', is_flag=True, default=False, help='Enable verbose logging')
    def run(params: dict, debug: bool):
        params = json.loads(params)
        bot = BotHandler(params=params, debug=debug)
        bot.handle()
    run()
