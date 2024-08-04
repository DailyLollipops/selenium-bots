from seleniumbot import SeleniumBot
from seleniumbot.enums import Driver, BotProxy
from bots.settings import settings
from loguru import logger
from abc import ABC, abstractmethod
import traceback
import sys


class BaseHandler(ABC):
    def __init__(self, driver: Driver, proxy: BotProxy = None, config: dict = {}, params: dict = {}) -> None:
        self.config = config
        self.logger = logger
        self.logger.add(f'{settings.LOG_DIR}/{config.get("id")}.log', level="INFO")
        self.scraper = SeleniumBot(
            hub_url=settings.HUB_URL,
            driver=driver,
            proxy=proxy,
            timeout=config.get('timeout', 30),
            proxymesh_username=settings.PROXYMESH_USERNAME,
            proxymesh_password=settings.PROXYMESH_PASSWORD,
        )
        self.logger.info(f"{driver} driver initialized")



    def preprocess_data(self):
        """
        Preprocess data.
        """
        pass



    @abstractmethod
    def run(self) -> dict:
        """
        Bot entry point function.
        """
        pass



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
            data['message'] = e
        finally:
            self.logger.info(f'Result: {data}')
            self.logger.info('Closing driver')
            self.scraper.close()
