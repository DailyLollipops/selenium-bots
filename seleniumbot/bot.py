from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.remote.webelement import WebElement

from .driverfactory import DriverFactory
from .dummylogger import DummyLogger
from .enums import Driver
from .proxyfactory import ProxyFactory
from .proxyserver import ProxyServer

from datetime import datetime
from logging import Logger

import time
import random
import signal

class SeleniumBot:
    def __init__(self, 
                 hub_url: str, 
                 driver: Driver, 
                 download_path = 'temp/downloads',
                 timeout: int = 30,
                 proxy: str = None,
                 disable_proxy_server: bool = False,
                 logger: Logger = None,
                 debug: bool = False,
                 **kwargs
                ) -> None:
        self.download_path = download_path
        self.logger = logger or DummyLogger()
        self.proxy_server = None
        if not disable_proxy_server and proxy:
            proxy_factory = ProxyFactory()
            proxy_factory.set_proxymesh_username(kwargs.get('proxymesh_username'))
            proxy_factory.set_proxymesh_password(kwargs.get('proxymesh_password'))
            bot_proxy = proxy_factory.get_proxy(proxy)
            self.proxy_server = ProxyServer(bot_proxy, debug=debug)
            proxy_server_port = self.proxy_server.start()
            proxy = f'http://runner:{proxy_server_port}'
        driver_factory = DriverFactory(logger=self.logger)
        driver_factory.set_hub_url(hub_url)
        self.driver = driver_factory.get_driver(driver, proxy=proxy)
        self.driver_wait = WebDriverWait(self.driver, timeout)
        signal.signal(signal.SIGINT, lambda signum, frame: self.close())

    def close(self):
        """
        Close necessary display and applications

        """
        if self.proxy_server:
            self.proxy_server.stop()
        if hasattr(self, 'driver'):
            self.driver.quit()

    def get_el(self, dom=None):
        """
        Gets the element to use. If the dom is not set, will return the selenium driver.

        :param dom: The element to use
        :return: The base element
        """
        return dom if dom else self.driver

    def get_element(self, selector: str = None, xpath: str = None, dom=None) -> WebElement:
        """
        Gets an element
        Selector or xpath must be supplied (selector takes precendence)

        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        :return: WebElement
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        if selector:
            criteria = By.CSS_SELECTOR
            locator = selector
        else:
            criteria = By.XPATH
            locator = xpath

        return self.get_el(dom).find_element(criteria, locator)

    def get_elements(self, selector: str = None, xpath: str = None, dom=None) -> list[WebElement]:
        """
        Gets an element
        Selector or xpath must be supplied (selector takes precendence)

        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        :return: WebElement
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        if selector:
            criteria = By.CSS_SELECTOR
            locator = selector
        else:
            criteria = By.XPATH
            locator = xpath

        return self.get_el(dom).find_elements(criteria, locator)

    def does_element_exist(self, selector: str = None, xpath: str = None, dom=None) -> bool:
        """
        Checks if selector exists from the DOM or driver
        Selector or xpath must be supplied (selector takes precendence)

        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        locator = {}
        if selector:
            locator['selector'] = selector
        else:
            locator['xpath'] = xpath

        try:
            self.get_element(**locator, dom=dom)
            return True
        except:
            return False
        
    def wait_to_be_clickable(self, selector: str = None, xpath: str = None) -> bool:
        """
        Wait for an element to be clickable. 
        Selector or xpath must be supplied (selector takes precendence)

        :param selector: CSS selector
        :param xpath: Element xpath
        :return: clickable
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        if selector:
            criteria = By.CSS_SELECTOR
            locator = selector
        else:
            criteria = By.XPATH
            locator = xpath

        try:
            self.driver_wait.until(EC.element_to_be_clickable((criteria, locator)))
            return True
        except TimeoutException:
            return False

    def wait_to_be_selectable(self, selector: str = None, xpath: str = None):
        """
        Wait for an element to be selectable. 
        Selector or xpath must be supplied (selector takes precendence)

        :param selector: CSS selector
        :param xpath: Element xpath
        :return: selectable
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        if selector:
            criteria = By.CSS_SELECTOR
            locator = selector
        else:
            criteria = By.XPATH
            locator = xpath

        try:
            return self.driver_wait.until(EC.element_to_be_selected((criteria, locator)))
        except TimeoutException:
            return None

    def wait_to_be_visible(self, selector: str = None, xpath: str = None):
        """
        Wait for an element to be loaded in the page. 
        Selector or xpath must be supplied (selector takes precendence)

        :param selector: CSS selector
        :param xpath: Element xpath
        :return: visible
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        if selector:
            criteria = By.CSS_SELECTOR
            locator = selector
        else:
            criteria = By.XPATH
            locator = xpath

        try:
            return self.driver_wait.until(EC.visibility_of_element_located((criteria, locator)))
        except TimeoutException:
            return None

    def wait_to_be_invisible(self, selector: str = None, xpath: str = None):
        """
        Wait for an element to be unloaded in the page. 
        Selector or xpath must be supplied (selector takes precendence)

        :param selector: CSS selector
        :param xpath: Element xpath
        :return: invisible
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        if selector:
            criteria = By.CSS_SELECTOR
            locator = selector
        else:
            criteria = By.XPATH
            locator = xpath

        try:
            return self.driver_wait.until(EC.invisibility_of_element_located((criteria, locator)))
        except TimeoutException:
            return None

    def fill_input(self, fill_string: str, selector: str = None, xpath: str = None, dom=None):
        """
        Fills the selector with the string provided. Ths will work for input text boxes.
        Selector or xpath must be supplied (selector takes precendence)

        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        locator = {}
        if selector:
            locator['selector'] = selector
        else:
            locator['xpath'] = xpath

        self.get_element(**locator, dom=dom).send_keys(fill_string)

    def clear_input(self, selector: str = None, xpath: str = None, dom=None):
        """
        Clears the field value. This will work for input text boxes.
        Selector or xpath must be supplied (selector takes precendence)

        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        locator = {}
        if selector:
            locator['selector'] = selector
        else:
            locator['xpath'] = xpath

        self.get_element(**locator, dom=dom).clear()

    def hit_enter_to_input(self, selector: str = None, xpath: str = None, dom=None):
        """
        Hits the enter key for the input field.
        Selector or xpath must be supplied (selector takes precendence)

        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        locator = {}
        if selector:
            locator['selector'] = selector
        else:
            locator['xpath'] = xpath

        self.get_element(**locator, dom=dom).send_keys(Keys.RETURN)

    def click_element(self, selector: str = None, xpath: str = None, dom=None):
        """
        Clicks an element.
        Selector or xpath must be supplied (selector takes precendence)

        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        locator = {}
        if selector:
            locator['selector'] = selector
        else:
            locator['xpath'] = xpath

        self.get_element(**locator, dom=dom).click()

    def right_click_element(self, selector: str = None, xpath: str = None, dom=None):
        """
        Right-clicks an element.
        Selector or xpath must be supplied (selector takes precendence)

        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        locator = {}
        if selector:
            locator['selector'] = selector
        else:
            locator['xpath'] = xpath

        element = self.get_element(**locator, dom=dom)
        ActionChains(self.driver).context_click(element).pause(random.randint(1, 3)).perform()

    def control_click_element(self, selector: str = None, xpath: str = None, dom=None):
        """
        Control + click an element.
        Selector or xpath must be supplied (selector takes precendence)

        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        locator = {}
        if selector:
            locator['selector'] = selector
        else:
            locator['xpath'] = xpath

        element = self.get_element(**locator, dom=dom)
        ActionChains(self.driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()

    def set_single_select_value(self, value: str = "", selector: str = None, xpath: str = None, dom=None):
        """
        Sets the dropdown value by option value.
        Selector or xpath must be supplied (selector takes precendence)

        :param value: Option value to set
        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        locator = {}
        if selector:
            locator['selector'] = selector
        else:
            locator['xpath'] = xpath

        el = self.get_element(**locator, dom=dom)
        drop_down = Select(el)
        drop_down.select_by_value(value)

    def set_single_select_by_label(self, label: str, selector: str = None, xpath: str = None, dom=None):
        """
        Sets the dropdown value by option label.
        Selector or xpath must be supplied (selector takes precendence)

        :param label: Option value to set
        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        locator = {}
        if selector:
            locator['selector'] = selector
        else:
            locator['xpath'] = xpath
        try:
            el = self.get_element(**locator, dom=dom)
            drop_down = Select(el)
            drop_down.select_by_visible_text(label)
        except Exception as e:
            pass

    def set_multiple_select_by_value(self, values: list[str], selector: str = None, xpath: str = None, dom=None):
        """
        Sets the dropdown value by option value.
        Selector or xpath must be supplied (selector takes precendence)

        :param value: Option value to set
        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        locator = {}
        if selector:
            locator['selector'] = selector
        else:
            locator['xpath'] = xpath

        el = self.get_element(**locator, dom=dom)
        drop_down = Select(el)
        for x in values:
            drop_down.select_by_value(x)

    def set_multiple_select_by_label(self, labels: list[str], selector: str = None, xpath: str = None, dom=None):
        """
        Sets the dropdown value by option value.
        Selector or xpath must be supplied (selector takes precendence)

        :param value: Option value to set
        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        locator = {}
        if selector:
            locator['selector'] = selector
        else:
            locator['xpath'] = xpath

        el = self.get_element(selector, dom)
        drop_down = Select(el)
        for x in labels:
            drop_down.select_by_visible_text(x)

    def accept_alert(self):
        """
        Accepts the alert if present
        """
        time.sleep(1)
        try:
            if EC.alert_is_present:
                Alert(self.driver).accept()
        except NoAlertPresentException:
            return

    def has_alert(self) -> bool:
        """
        Checks if alert is present

        :return: returns True if there is at least 1
        """

        time.sleep(1)
        if EC.alert_is_present is not False:
            return True
        else:
            return False

    def check_for_alert(self):
        """
        Checks if alert is present

        :return: returns True if there is at least 1
        """

        time.sleep(1)
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            return True
        except TimeoutException:
            return False

    def get_inner_text(self, selector: str = None, xpath: str = None, dom=None) -> str:
        """
        Gets an element text value.
        Selector or xpath must be supplied (selector takes precendence)

        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        locator = {}
        if selector:
            locator['selector'] = selector
        else:
            locator['xpath'] = xpath

        return self.get_element(**locator, dom=dom).text

    def get_dropdown_text(self, selector: str = None, xpath: str = None, dom=None) -> str:
        """
        Gets the dropdown selected text
        Selector or xpath must be supplied (selector takes precendence)

        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        locator = {}
        if selector:
            locator['selector'] = selector
        else:
            locator['xpath'] = xpath

        select = Select(self.get_element(**locator, dom=dom))
        selected_option = select.first_selected_option
        return selected_option.text
    
    def get_attribute(self, attribute: str, selector: str = None, xpath: str = None, dom=None) -> str:
        """
        Gets the src of an element
        Selector or xpath must be supplied (selector takes precendence)

        :param attribute: Element attribute to retrieve
        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        locator = {}
        if selector:
            locator['selector'] = selector
        else:
            locator['xpath'] = xpath

        return self.get_element(**locator, dom=dom).get_attribute(attribute)

    def set_attribute(self, attribute: str, value: str, selector: str = None, xpath: str = None, dom=None):
        """
        Sets an attribute value for an element
        Selector or xpath must be supplied (selector takes precendence)

        :param value: Option value to set
        :param selector: CSS selector
        :param xpath: Element xpath
        :param dom: the base element
        """
        if not selector and not xpath:
            raise Exception("No selector or xpath supplied")
        
        locator = {}
        if selector:
            locator['selector'] = selector
        else:
            locator['xpath'] = xpath

        element = self.get_element(**locator, dom=dom)
        return self.driver.execute_script("arguments[0].setAttribute('{}','{}')".format(attribute, value), element)

    def remove_element_attribute(self, attribute: str, el=None, selector: str = "", dom=None):
        """
        Synchronously Executes JavaScript in the current window/frame.

        :param _command: The JavaScript to execute.
        :param args: Any applicable arguments for your JavaScript.
        :return:
        """

        element = el if el else self.get_element(selector, dom)
        return self.driver.execute_script("arguments[0].removeAttribute('{}')".format(attribute), element)
    
    def get_screen_shot(self) -> str:
        """
        Gets the screen shot of the current view as BASE64

        :return: the base64 encoded image
        """
        return self.driver.get_screenshot_as_base64()

    def save_screenshot(self, file_name: str):
        """
        Saves the screenshot as file

        :param file_name:
        """
        self.driver.get_screenshot_as_file(file_name)

    def maximize_window(self):
        """
        Try to maximamize window

        :return:
        """
        try:
            self.driver.maximize_window()
        except Exception:
            pass

    def set_window_size(self, height: int, width: int):
        """
        Re-sizes the window view to a fixed height and width

        :param height: the height to be set
        :param width: the width to be set
        :return:
        """
        self.driver.set_window_size(width, height)

    def go_back(self):
        """
        Gos back to previous browser history

        :return:
        """
        self.driver.back()

    def go_to_url(self, url: str):
        """
        Go to specified url

        :return:
        """
        self.driver.get(url)

    def switch_tab(self, tab: int):
        """
        Change tab in browser

        :param tab: index of the window or tab in browser
        :return:
        """
        self.driver.switch_to.window(self.driver.window_handles[tab])

    def open_and_switch_tab(self, close_previous: bool = True):
        """
        Open a new tab and switch to the newly created tab

        :param close_previous: Close previous tab after switching
        """
        self.driver.switch_to.new_window("tab")
        self.driver.implicitly_wait(20)

        self.driver.switch_to.window(self.driver.window_handles[0])
        if close_previous:
            self.close_tab()

        time.sleep(random.randint(1, 2))
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def close_tab(self):
        """
        Close current window or tab

        :return:
        """
        self.driver.close()

    def hit_escape(self):
        """
        Press escape button

        :param selector:
        :param dom:
        :return:
        """
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

    def scroll_to_bottom(self):
        """
        Scroll to the bottom of the site to load data from infinite scroll
        :return:
        """
        SCROLL_PAUSE_TIME = 0.5

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def refresh(self):
        """
        Refresh current page

        :return:
        """
        self.driver.refresh()

    def execute_script(self, _command: str, *args):
        """
        Synchronously Executes JavaScript in the current window/frame.

        :param _command: The JavaScript to execute.
        :param args: Any applicable arguments for your JavaScript.
        :return:
        """

        return self.driver.execute_script(_command, args)

    def go_to_iframe(self, iframe):
        """
        Focus on the iframe to access elements inside it

        :param iframe: xpath of the iframe
        :return:
        """
        self.driver.switch_to.frame(self.get_element_by_xpath(iframe))

    def go_to_iframe_selector(self, iframe):
        """
        Focus on the iframe to access elements inside it

        :param iframe: selector of the iframe
        :return:
        """
        self.driver.switch_to.frame(self.get_element(iframe))

    def get_current_url(self) -> str:
        """
        Returns the current URL

        :return:
        """
        return self.driver.current_url

    def get_browser_version(self):
        """
        Gets the browser version
        :return:
        """

        browser_ver = self.driver.capabilities.get("browserName", "")

        if "browserVersion" in self.driver.capabilities:
            return browser_ver + " " + self.driver.capabilities["browserVersion"]
        elif "version" in self.driver.capabilities:
            return browser_ver + " " + self.driver.capabilities["version"]

        return browser_ver

    def save_screenshot_by_time(self):
        """
        Saves the screenshot as file

        """

        self.resize_window()
        current_datetime = datetime.strftime(datetime.now(), "%m-%d-%Y-%H-%M-%S")
        file_name = "{}.png".format(current_datetime)
        self.driver.get_screenshot_as_file(file_name)

    def save_screenshot_by_time_id(self, _id: str):
        """
        Save screenshot as file with ID and time

        :param _id:
        :return:
        """

        self.resize_window()
        current_datetime = datetime.strftime(datetime.now(), "%m-%d-%Y-%H-%M-%S")
        file_name = "{}-{}.png".format(_id, current_datetime)
        self.driver.get_screenshot_as_file(file_name)

    def get_page_source(self):
        """
        Returns the page source

        :return:
        """
        return self.driver.page_source

    def is_visible(self, selector: str, dom=None):
        """
        Checks if the element is visible or not

        :param selector:
        :param dom:
        :return:
        """
        return self.get_element(selector, dom).is_displayed()


    def control_hit_enter_selector(self, selector: str, dom=None):
        """
        Control + hit enter the selector

        :param selector: CSS selector
        :param dom: the base element to find the CSS selector
        """
        self.get_element(selector, dom).send_keys(Keys.CONTROL + Keys.RETURN)

    def go_to_default_frame(self):
        """
        Come out of all the frames and switch the focus at the page
        :return:
        """
        self.driver.switch_to.default_content()

    def scroll_to_top(self):
        """
        Scroll to the top of the site
        :return:
        """

        self.driver.find_element(By.TAG_NAME, "html").send_keys(Keys.CONTROL + Keys.HOME)

    def scroll_into_view(self, elem: WebElement):
        """
        Scroll the elements into view
        :param elem: the webelement to scroll into view
        :return:
        """
        return self.driver.execute_script("arguments[0].scrollIntoView(true);", elem)

    def get_downloadable_files(self) -> dict:
        """
        Get a list of immediate snapshot of file names that are currently in the directory.

        :return: dict of files
        """
        return self.driver.get_downloadable_files()
    
    def download_remote_file(self, remote_file: str, directory: str = None):
        """
        Download a file from remote webdriver

        :param remote_file: Remote file name
        :param directory: Target directory, default to driver download location
        """
        if not directory:
            directory = self.download_path
        return self.driver.download_file(remote_file, directory)
    
    def wait_file_to_be_downloadad(self, file_name: str, timeout: int = 30):
        """
        Wait to for file to be downloaded

        :param file_name: File name
        :param timeout: Download timeout
        """
        WebDriverWait(self.driver, timeout).until(lambda d: file_name in d.get_downloadable_files())
