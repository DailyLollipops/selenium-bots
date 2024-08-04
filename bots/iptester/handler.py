from bots.iptester.botconfig import config
from seleniumbot.enums import Driver, BotProxy
from bots.basehandler import BaseHandler, DictParamType

import click

class BotHandler(BaseHandler):
    def __init__(self, params: dict = {}, debug: bool = False) -> None:
        super().__init__(Driver.CHROME, proxy=BotProxy.FREE_HTTPS, config=config, params=params, debug=debug)
        
    def run(self):
        """
        Bot entry point function.
        """
        main_url = self.config.get('mainUrl')
        ipv4_xpath = self.config.get('ipV4Xpath')
        ipv6_xpath = self.config.get('ipV6Xpath')
        self.scraper.go_to_url(main_url)
        self.scraper.wait_to_be_visible(xpath=ipv4_xpath)
        self.scraper.wait_to_be_visible(xpath=ipv6_xpath)
        ipv4 = self.scraper.get_inner_text(xpath=ipv4_xpath)
        ipv6 = self.scraper.get_inner_text(xpath=ipv6_xpath)
        result = {
            'ipv4': ipv4,
            'ipv6': ipv6
        }
        return result


if __name__ == '__main__':
    @click.command()
    @click.option('--params', '-p', type=DictParamType(), default={}, help='Bot handler parameters')
    @click.option('--debug', '-d', is_flag=True, default=False, help='Enable verbose logging')
    def run(params: dict, debug: bool):
        bot = BotHandler(params=params, debug=debug)
        bot.handle()
    run()
