from seleniumbot import SeleniumBot
from seleniumbot.proxyfactory import ProxyFactory
from seleniumbot.proxyserver import ProxyServer
from seleniumbot.enums import Driver, BotProxy
from bots.settings import settings

from loguru import logger

import traceback


class RotatingProxyMixin:
    config: dict
    driver: Driver
    scraper: SeleniumBot
    proxy_server: ProxyServer
    proxy_factory: ProxyFactory
    bot_proxy: BotProxy
    logger = logger
    debug: bool
    max_retries = 10


    def do_run(self) -> dict:
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
            self.logger.info('Closing driver')
            self.scraper.close()
            if self.proxy_server:
                self.proxy_server.stop()
                del self.proxy_server
            return data


    
    def handle(self):
        if 'free' in self.bot_proxy.value:
            retries = self.max_retries
            while retries > 0:
                result = self.do_run()
                if result.get('success'):
                    return result
                retries -= 1
                self.logger.info(f'Run failed. Rotating proxy. Retries left: {retries}')
                if retries != 0:
                    proxy = self.proxy_factory.get_proxy(self.bot_proxy)
                    self.proxy_server = ProxyServer(proxy, debug=self.debug)
                    proxy_server_port = self.proxy_server.start()
                    proxy_server_url = f'http://runner:{proxy_server_port}'
                    self.scraper = SeleniumBot(
                        hub_url=settings.HUB_URL,
                        driver=self.driver,
                        proxy=proxy_server_url,
                        timeout=self.config.get('timeout', 30),
                        debug=self.debug
                    )
            else:
                result = {
                    'success': False,
                    'message': 'No more retries left',
                    'data': {}
                }
                self.logger.info(f'Result: {result}')
                return result
        else:
            raise NotImplementedError(f'Rotating proxy mixin not implemented for {self.bot_proxy}')
