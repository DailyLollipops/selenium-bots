from bs4 import BeautifulSoup
from loguru import logger
from .enums import BotProxy
import requests


class ProxyFactory:
    PROXYMESH_USERNAME = ''
    PROXYMESH_PASSWORD = ''


    def __init__(self) -> None:
        pass



    def set_proxymesh_username(self, username: str):
        """
        Set proxymesh username

        :param username: Proxymesh username
        """
        self.PROXYMESH_USERNAME = username



    def set_proxymesh_password(self, password: str):
        """
        Set proxymesh password

        :param password: Proxymesh password
        """
        self.PROXYMESH_PASSWORD = password



    def get_proxy(self, proxy: BotProxy) -> str:
        if proxy is None: 
            return None
        if proxy == BotProxy.FREE:
            return self.__get_free_proxy()
        elif proxy == BotProxy.FREE_GOOGLE:
            return self.__get_free_proxy(only_google=True)
        elif proxy == BotProxy.FREE_HTTPS:
            return self.__get_free_proxy(only_https=True)
        elif proxy == BotProxy.FREE_GOOGLE_HTTPS:
            return self.__get_free_proxy(only_google=True, only_https=True)
        elif proxy == BotProxy.FREE_US:
            return self.__get_free_proxy(country='United States')
        elif proxy == BotProxy.FREE_US_GOOGLE:
            return self.__get_free_proxy(country='United States', only_google=True)
        elif proxy == BotProxy.FREE_US_HTTPS:
            return self.__get_free_proxy(country='United States', only_https=True)
        elif proxy == BotProxy.FREE_US_GOOGLE_HTTPS:
            return self.__get_free_proxy(country='United States', only_google=True, only_https=True)
        elif 'proxymesh' in proxy.value:
            return self.__get_proxymesh_proxy(proxy)



    def __get_free_proxy(self, country: str = 'all', only_google: bool = False, only_https: bool = False) -> str:
        """
        Get a free proxy from `https://free-proxy-list.net/`

        :param country: country to get proxy from, if 'all' get anything. Defaults to all.
        :param only_google: Only google allowed
        :param only_https: Only https enabled
        :return: proxy
        :raises: Exception if no proxy is returned
        """
        response = requests.get('https://free-proxy-list.net/')
        soup = BeautifulSoup(response.text, 'lxml')
        rows = soup.select('table > tbody > tr')
        for i in range(len(rows)):
            ip_address = soup.select_one(f'table > tbody > tr:nth-child({i+1}) > td:nth-child(1)').text
            port = soup.select_one(f'table > tbody > tr:nth-child({i+1}) > td:nth-child(2)').text
            country_value = soup.select_one(f'table > tbody > tr:nth-child({i+1}) > td:nth-child(4)').text
            google_value = soup.select_one(f'table > tbody > tr:nth-child({i+1}) > td:nth-child(6)').text
            https_value = soup.select_one(f'table > tbody > tr:nth-child({i+1}) > td:nth-child(7)').text
            if country != 'all' and country_value != country:
                continue
            if only_google and google_value.lower() == 'no':
                continue
            if only_https and https_value.lower() == 'no':
                continue
            logger.info(f'Got proxy: {ip_address}:{port}')
            return f'{ip_address}:{port}'
        raise Exception('Got no proxy')
    


    def __get_proxymesh_proxy(self, bot_proxy: BotProxy) -> str:
        """
        Return an equivalent proxymesh proxy of given botproxy

        :param bot_proxy: Proxymesh bot proxy
        :return: proxy
        """
        proxymesh_mapping = {
            BotProxy.PROXYMESH_AU: 'au.proxymesh.com:31280',
            BotProxy.PROXYMESH_CA: 'us-ca.proxymesh.com:31280',
            BotProxy.PROXYMESH_CH: 'ch.proxymesh.com:31280',
            BotProxy.PROXYMESH_DC: 'us-dc.proxymesh.com:31280',
            BotProxy.PROXYMESH_DE: 'de.proxymesh.com:31280',
            BotProxy.PROXYMESH_FL: 'us-fl.proxymesh.com:31280',
            BotProxy.PROXYMESH_FR: 'fr.proxymesh.com:31280',
            BotProxy.PROXYMESH_IL: 'us-il.proxymesh.com:31280',
            BotProxy.PROXYMESH_IN: 'in.proxymesh.com:31280',
            BotProxy.PROXYMESH_JP: 'jp.proxymesh.com:31280',
            BotProxy.PROXYMESH_NL: 'nl.proxymesh.com:31280',
            BotProxy.PROXYMESH_NY: 'us-ny.proxymesh.com:31280',
            BotProxy.PROXYMESH_OPEN: 'open.proxymesh.com:31280',
            BotProxy.PROXYMESH_SG: 'sg.proxymesh.com:31280',
            BotProxy.PROXYMESH_TX: 'us-tx.proxymesh.com:31280',
            BotProxy.PROXYMESH_UK: 'uk.proxymesh.com:31280',
            BotProxy.PROXYMESH_US: 'usisp.proxymesh.com:31280',
            BotProxy.PROXYMESH_WA: 'us-wa.proxymesh.com:31280',
            BotProxy.PROXYMESH_WORLD: 'world.proxymesh.com:31280'
        }
        proxymesh_proxy = proxymesh_mapping.get(bot_proxy)
        if not proxymesh_proxy:
            raise Exception(f'{bot_proxy} is not a valid proxymesh proxy')
        proxy = f'http://{self.PROXYMESH_USERNAME}:{self.PROXYMESH_PASSWORD}.{proxymesh_proxy}'
        logger.info(f'Got proxy: http://****:****@{proxymesh_proxy}')
        return proxy
