# -*- coding: utf-8 -*-
from scrapy import signals
from .http import SeleniumRequest, SeleniumResponse
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

class SeleniumCallbackException(Exception):
    pass

class SeleniumMiddleware:
    def __init__(self, settings):
        headless = settings.get('SELENIUM_HEADLESS', True)
        driver_path = settings.get('CHROME_DRIVER_PATH', None)
        self._cookies_set = False
        self._instantiate_driver(driver_path, headless)

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler.settings)
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware

    def _get_page(self, request):
        self.driver.get(request.url)
        if not self._cookies_set:
            self._add_cookie(request)

    def _instantiate_driver(self, driver_path, headless):
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-dev-shm-usage')
        if driver_path:
            self.driver = webdriver.Chrome(executable_path=self.driver_path, chrome_options=options)
        else:
            self.driver = webdriver.Chrome(chrome_options=options)
        
    def _add_cookie(self, request):
        if isinstance(request.cookies, list):
            for cookie in request.cookies:
                self.driver.add_cookie(cookie)
        elif isinstance(request.cookies, dict):
            self.driver.add_cookie(request.cookies)
        self._cookies_set = True
        self.driver.get(request.url)

    def _handle_callback(self, request):
        """Execute Selenium callback with keyword arguments, if set"""
        if callable(request.selenium_callback):
            if request.selenium_cb_kwargs:
                request.selenium_callback(self.driver, **request.selenium_cb_kwargs)
            else:
                request.selenium_callback(self.driver)
        elif request.selenium_callback == None:
            return
        else:
            raise SeleniumCallbackException("selenium_callback must be callable or None")

    def process_request(self, request, spider):
        if not isinstance(request, SeleniumRequest):
            return None
        self._get_page(request)
        self._handle_callback(request)
        response = SeleniumResponse.from_driver(self.driver, request)
        return response

    def spider_closed(self):
        """Quit Selenium driver when spider is closing"""
        self.driver.quit()
