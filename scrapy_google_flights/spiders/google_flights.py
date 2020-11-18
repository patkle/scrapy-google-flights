import pkgutil
import json
from time import sleep

from scrapy import Spider
from web_poet.pages import ItemWebPage

from ..http import PyppeteerRequest
from ..middlewares import PyppeteerMiddleware

# set this cookie to avoid dealing with cookie warning messages
consent_cookie = {
    'url': 'https://www.google.com',
    'name': 'CONSENT',
    'value': "YES+US.en+20200218-08-0",
    'SameSite':"None",
    "domain": "",
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
                'price': self.price(flight),
                'operator': self.operator(flight),
                'departure': self.departure(flight),
                'arrival': self.arrival(flight)
            }

async def load_all_flights(page):
    await page.evaluate('''()=> {
        function getElementByXpath(path) {
            return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        }

        getElementByXpath('//div[@jsaction="click:yQf8Td"]').click();
    }
    ''')
    sleep(10)

class GoogleFlightsSpider(Spider):
    name = 'google_flights'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            PyppeteerMiddleware: 100,
            'scrapy_poet.InjectionMiddleware': 543,
        }
    }

    def __init__(self):
        f = pkgutil.get_data("scrapy_google_flights", "resources/searches.json")
        self.searches = json.loads(f)

    def start_requests(self):
        for search in self.searches:
            yield PyppeteerRequest(
                self._get_flight_url(search),
                pyppeteer_callback=load_all_flights,
                cookies=consent_cookie,
                dont_filter=True,
            )
    
    def _get_flight_url(self, flight_data):
        origin = flight_data['origin']
        destination = flight_data['destination']
        return f'https://www.google.com/flights#flt={origin}.{destination}.2021-02-10' + ";tt:o"

    def parse(self, response, page: FlightPage):
        return page.to_item()
