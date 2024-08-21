from seleniumbot import SeleniumBot
from seleniumbot.proxyfactory import ProxyFactory
from seleniumbot.proxyserver import ProxyServer
from seleniumbot.enums import Driver, BotProxy

from bots.common.exceptions import ValidationError
from bots.common.parameter import Parameter
from bots.common.settings import settings
from bots.common.utils import dictutils, contextutils

from loguru import logger
from abc import ABC, abstractmethod

import uuid
import signal
import sys
import time
import traceback


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
        self.proxy_server = None
        self.debug = debug
        self.driver = driver
        self.proxy = proxy
        self.scraper = None
        self.interrupted = False

        trace_id = str(uuid.uuid4())
        self.logger = logger
        self.logger = self.logger.bind(trace_id=trace_id)
        self.logger.remove()
        log_format = '<green>{time}</green> | <level>{level}</level> | <blue>{extra[trace_id]}</blue> | <cyan>{name}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>'
        self.logger.add(
            f'{settings.LOG_DIR}/{config.get("id")}.log', 
            level="INFO", 
            format=log_format
        )
        logger.add(
            sys.stdout, 
            format=log_format,
            colorize=True
        )

        self.logger.info(f'Starting bot params={params}')
        proxy_server_url = ''
        if proxy:
            self.proxy_factory = ProxyFactory(logger=self.logger)
            self.proxy_factory.set_proxymesh_username(settings.PROXYMESH_USERNAME)
            self.proxy_factory.set_proxymesh_password(settings.PROXYMESH_PASSWORD)
            bot_proxy = self.proxy_factory.get_proxy(proxy)
            self.proxy_server = ProxyServer(bot_proxy, logger=self.logger, debug=debug)
            proxy_server_port = self.proxy_server.start()
            proxy_server_url = f'http://runner:{proxy_server_port}'
        self.scraper = SeleniumBot(
            hub_url=settings.HUB_URL,
            driver=driver,
            download_path=settings.DOWNLOAD_DIR,
            proxy=proxy_server_url,
            timeout=config.get('timeout', 30),
            page_timeout=config.get('pageTimeout', 30),
            disable_proxy_server=True,
            logger=self.logger,
            debug=debug
        )
        self.logger.info(f"{driver} driver initialized")
        signal.signal(signal.SIGINT, self.cleanup)



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
        start_time = time.time()

        try:
            self.preprocess_data()
            result = self.run() or {}
            data['success'] = True
            data['message'] = 'Bot ran successfully'
            data['data'] = result
        except Exception as e:
            self.logger.error(traceback.format_exc())
            data['success'] = False
            data['message'] = str(e)
        finally:
            if self.interrupted:
                data['success'] = False
                data['message'] = 'Bot run interrupted'
            if not self.interrupted:
                self.cleanup()
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.logger.info(f'Elapsed time: {elapsed_time}')
            self.logger.info(f'Result: {data}')



    def cleanup(self, signum=None, frame=None):
        if signum == signal.SIGINT:
            self.logger.info('Interrupted')
            self.interrupted = True
        if self.proxy_server:
            try:
                with contextutils.timeout_sync(10):
                    self.proxy_server.stop(wait=False)
            except TimeoutError:
                self.logger.info('Proxy server shutdown timeout')
        if self.scraper:
            self.logger.info('Closing driver')
            self.scraper.close()
        if self.interrupted:
            sys.exit(0)
