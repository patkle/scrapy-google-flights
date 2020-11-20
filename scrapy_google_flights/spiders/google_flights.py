import pkgutil
import json
import asyncio
from typing import Optional, Dict
from parsel.selector import Selector, SelectorList

from scrapy import Spider
from web_poet.pages import ItemWebPage

from ..http import PyppeteerRequest
from ..middlewares import PyppeteerMiddleware


class FlightPage(ItemWebPage):
    """Extract flights from Google Flight search result page"""
    @property
    def flights(self) -> SelectorList:
        """Returns SelectorList for every flight on given webpage"""
        return self.xpath('//div[@jsaction="click:O1htCb;"]')

    def price(self, flight: Selector) -> Optional[str]:
        return flight.xpath('.//div[@class="YMlIz tu4g7b"]/span/text()').get()

    def operator(self, flight: Selector) -> Optional[str]:
        return flight.xpath('.//div[@class="TQqf0e sSHqwe tPgKwe ogfYpf"]/span/text()').get()

    def departure(self, flight: Selector) -> Optional[str]:
        return flight.xpath('.//g-bubble[1]').xpath('.//span[@class="eoY5cb"]/text()').get()

    def arrival(self, flight: Selector) -> Optional[str]:
        return flight.xpath('.//g-bubble[2]').xpath('.//span[@class="eoY5cb"]/text()').get()

    def duration(self, flight: Selector) -> Optional[str]:
        return flight.xpath('.//div[@class="gvkrdb AdWm1c tPgKwe ogfYpf"]/text()').get()

    def stops(self, flight: Selector) -> Optional[str]:
        # TODO:
        pass

    def to_item(self) -> Dict[str, Optional[str]]:
        for flight in self.flights:
            yield {
                'price': self.price(flight),
                'operator': self.operator(flight),
                'departure': self.departure(flight),
                'arrival': self.arrival(flight)
            }

# set consent cookie for google.com to avoid dealing with cookie pop-ups
consent_cookie = {
    'url': 'https://www.google.com',
    'name': 'CONSENT',
    'value': "YES+US.en+20200218-08-0",
    'SameSite': "None",
    "domain": "",
    'path': '/',
}

async def load_all_flights(page) -> None:
    """Callback passed to PyppeteerMiddleware to load all flights before returning a respone"""
    # Selects and clicks button to show all flights 
    await page.evaluate('''()=> {
        function getElementByXpath(path) {
            return document.evaluate(
                path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null
            ).singleNodeValue;
        }
        getElementByXpath('//div[@jsaction="click:yQf8Td"]').click();
    }
    ''')
    # wait for 10 seconds to ensure that all flights are loaded
    await asyncio.sleep(10)


class GoogleFlightsSpider(Spider):
    """ """
    name = 'google_flights'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            PyppeteerMiddleware: 100,
            'scrapy_poet.InjectionMiddleware': 543,
        }
    }

    def __init__(self) -> None:
        """ """
        f = pkgutil.get_data("scrapy_google_flights", "resources/searches.json")
        self.searches = json.loads(f)

    def start_requests(self) -> PyppeteerRequest:
        """Generate PyppeteerRequests for every search in self.searches"""
        for search in self.searches:
            yield PyppeteerRequest(
                self._get_flight_url(search),
                pyppeteer_callback=load_all_flights,
                cookies=consent_cookie,
                dont_filter=True,
            )

    def _get_flight_url(self, flight_data: Dict) -> str:
        origin = flight_data['origin']
        destination = flight_data['destination']
        return f'https://www.google.com/flights#flt={origin}.{destination}.2021-02-10' + ";tt:o"

    async def parse(self, response, page: FlightPage):
        return page.to_item()
