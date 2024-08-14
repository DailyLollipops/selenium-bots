from seleniumbot import SeleniumBot
from seleniumbot.proxyfactory import ProxyFactory
from seleniumbot.proxyserver import ProxyServer
from seleniumbot.enums import Driver, BotProxy

from bots.common.exceptions import ValidationError
from bots.common.parameter import Parameter
from bots.common.settings import settings
from bots.common.utils import dictutils

from loguru import logger
from abc import ABC, abstractmethod

import traceback
import re


class BaseHandler(ABC):
    def __init__(self, 
                 driver: Driver, 
                 proxy: BotProxy = None, 
                 config: dict = {}, 
                 params: dict = {}, 
                 debug: bool = False
                ) -> None:
        self.parameters = params or {}
        self.config = config
        self.logger = logger
        self.proxy_server = None
        self.logger.add(f'{settings.LOG_DIR}/{config.get("id")}.log', level="INFO")
        self.logger.info(f'Starting bot params={params}')
        proxy_server_url = ''
        if proxy:
            proxy_factory = ProxyFactory()
            proxy_factory.set_proxymesh_username(settings.PROXYMESH_USERNAME)
            proxy_factory.set_proxymesh_password(settings.PROXYMESH_PASSWORD)
            bot_proxy = proxy_factory.get_proxy(proxy)
            self.proxy_server = ProxyServer(bot_proxy, debug=debug)
            proxy_server_port = self.proxy_server.start()
            proxy_server_url = f'http://runner:{proxy_server_port}'
        self.scraper = SeleniumBot(
            hub_url=settings.HUB_URL,
            driver=driver,
            proxy=proxy_server_url,
            timeout=config.get('timeout', 30),
            proxymesh_username=settings.PROXYMESH_USERNAME,
            proxymesh_password=settings.PROXYMESH_PASSWORD,
            debug=debug
        )
        self.logger.info(f"{driver} driver initialized")



    def validate_parameters(self):
        """
        Validate parameters from config
        """
        if not (parameters := dictutils.get(self.config, 'parameters')):
            return
        self.logger.info('Validating parameters')
        for name, rules in parameters.items():
            self.logger.info(rules)
            if not (param_type := rules.pop('param_type')):
                raise ValidationError(f'Unknown param type for {name}')
            param = Parameter(name=name, param_type=param_type, **rules)
            param.validate(self.parameters.get(name, None))            



    def preprocess_data(self):
        """
        Preprocess data.
        """
        self.validate_parameters()



    @abstractmethod
    def run(self) -> dict:
        """
        Bot entry point function.
        """
        self.validate_parameters()



    def handle(self) -> dict:
        data = {
            'success': False,
            'message': '',
            'data': {}
        }
        try:
            self.preprocess_data()
            result = self.run() or {}
            data['success'] = True
            data['message'] = 'Bot ran successfully'
            data['data'] = result
        except KeyboardInterrupt:
            self.logger.info('CTRL+C detected')
            data['success'] = False
            data['message'] = 'Bot run interrupted'
        except Exception as e:
            self.logger.error(traceback.format_exc())
            data['success'] = False
            data['message'] = str(e)
        finally:
            self.logger.info(f'Result: {data}')
            if self.proxy_server:
                self.logger.info('Stopping proxy server')
                self.proxy_server.stop()
            self.logger.info('Closing driver')
            self.scraper.close()
