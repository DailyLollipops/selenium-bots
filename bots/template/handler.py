from botconfig import config
from seleniumbot.enums import Driver
from bots.basehandler import BaseHandler, DictParamType

import click

class BotHandler(BaseHandler):
    def __init__(self, params: dict = {}) -> None:
        super().__init__(Driver.CHROME, config=config, params=params)
        
    def run(self):
        """
        Bot entry point function.
        """
        pass


if __name__ == '__main__':
    @click.command()
    @click.option('--params', type=DictParamType(), default={}, help='Bot handler parameters')
    def run(params: dict):
        bot = BotHandler(params=params)
        bot.handle()
    run()
