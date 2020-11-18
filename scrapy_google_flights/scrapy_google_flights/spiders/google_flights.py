import pkgutil
import json
from time import sleep

from scrapy import Spider
from web_poet.pages import ItemWebPage

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ..http import SeleniumRequest
from ..middlewares import SeleniumMiddleware

# set this cookie to avoid dealing with cookie warning messages
consent_cookie = {
    'name': 'CONSENT',
    'value': "YES+US.en+20200218-08-0",
    'SameSite':"None",
    "domain": "",
    "expires": "",
    'path': '/',
    'httpOnly': False,
    'HostOnly': False,
    'Secure': False
}

class FlightPage(ItemWebPage):
    @property
    def flights(self):
        return self.xpath('//div[@jsaction="click:O1htCb;"]')

    def price(self, flight):
        return flight.xpath('.//div[@class="YMlIz tu4g7b"]/span/text()').get()

    def operator(self, flight):
        return flight.xpath('.//div[@class="TQqf0e sSHqwe tPgKwe ogfYpf"]/span/text()').get()

    def departure(self, flight):
        return flight.xpath('.//g-bubble[1]').xpath('.//span[@class="eoY5cb"]/text()').get()
        
    def arrival(self, flight):
        return flight.xpath('.//g-bubble[2]').xpath('.//span[@class="eoY5cb"]/text()').get()

    def duration(self, flight):
        return flight.xpath('.//div[@class="gvkrdb AdWm1c tPgKwe ogfYpf"]/text()').get()

    def stops(self, flight):
        # TODO:
        pass 

    def to_item(self):
        for flight in self.flights:
            yield {
                'url': self.url,
                'price': self.price(flight),
                'operator': self.operator(flight),
                'departure': self.departure(flight),
                'arrival': self.arrival(flight)
            }

def load_all_flights(driver):
    more_flights = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located(
                (By.XPATH, '//div[@jsaction="click:yQf8Td"]')
        )
    )
    more_flights.click()
    sleep(10)

class GoogleFlightsSpider(Spider):
    name = 'google_flights'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            SeleniumMiddleware: 100,
            'scrapy_poet.InjectionMiddleware': 543,
        }
    }

    def __init__(self):
        f = pkgutil.get_data("scrapy_google_flights", "resources/searches.json")
        self.searches = json.loads(f)

    def start_requests(self):
        for search in self.searches:
            yield SeleniumRequest(
                self._get_flight_url(search),
                selenium_callback=load_all_flights,
                cookies=consent_cookie,
                dont_filter=True,
            )
    
    def _get_flight_url(self, flight_data):
        origin = flight_data['origin']
        destination = flight_data['destination']
        return f'https://www.google.com/flights#flt={origin}.{destination}.2021-02-10' + ";tt:o"

    def parse(self, response, page: FlightPage):
        return page.to_item()
