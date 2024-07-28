from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options as FireFoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.proxy import Proxy, ProxyType
from .enums import Driver
from loguru import logger

class DriverFactory:
    HUB_URL = ''


    def __init__(self, hub_url: str = 'http://selenium-hub:4444/wd/hub') -> None:
        self.HUB_URL = hub_url



    def set_hub_url(self, url):
        """
        Set hub url

        :param url: Selenium grid hub url
        """
        self.HUB_URL = url
        


    def get_driver(self, driver: Driver, proxy: str = None) -> webdriver.Remote:
        logger.info(f'Connecting to {self.HUB_URL}')
        if driver == Driver.CHROME:
            return self.__initialize_chrome(proxy=proxy)
        elif driver == Driver.FIREFOX:
            return self.__initialize_firefox(proxy=proxy)



    def __initialize_firefox(self, proxy: str = None) -> webdriver.Remote:
        options = FireFoxOptions()
        options.set_preference('network.negotiate-auth.allow-proxies', True)
        options.set_preference('network.captive-portal-service.enabled', False)
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('useAutomationExtension', False)
        options.set_preference('download.directory_upgrade', True)
        options.set_preference('safebrowsing.enabled', True)
        options.set_preference('download.prompt_for_download', False)
        options.set_preference('plugins.always_open_pdf_externally', True)
        options.set_preference('pdfjs.disabled', True)
        options.set_preference('helperApps.alwaysAsk.force', False)
        options.set_preference('print.always_print_silent', True)
        options.set_preference('browser.download.folderList', 2)
        options.set_preference('browser.download.manager.showWhenStarting', False)
        options.set_preference('browser.download.dir', "")
        options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/x-gzip')

        if proxy:
            proxy = Proxy({
                'proxyType': ProxyType.MANUAL,
                'httpProxy': proxy,
                'sslProxy': proxy,
                'noProxy': ''
            })
            options.proxy = proxy
        driver = webdriver.Remote(command_executor=self.HUB_URL, options=options)
        return driver
    


    def __initialize_chrome(self, proxy: str = None) -> webdriver.Remote:
        options = ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--enable-javascript')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--dns-prefetch-disable')
        if proxy:
            proxy = Proxy({
                'proxyType': ProxyType.MANUAL,
                'httpProxy': proxy,
                'sslProxy': proxy,
                'noProxy': ''
            })
            options.proxy = proxy
        driver = webdriver.Remote(command_executor=self.HUB_URL, options=options)
        return driver
    