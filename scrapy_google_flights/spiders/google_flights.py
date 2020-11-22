import pkgutil
import json
import asyncio
from typing import Optional, Dict, Tuple, Union
from datetime import date, timedelta
from dateutil.parser import parse

from scrapy import Spider
from parsel.selector import Selector, SelectorList
from web_poet.pages import ItemWebPage

from ..http import PyppeteerRequest
from ..middlewares import PyppeteerMiddleware


class FlightPage(ItemWebPage):
    """Extraction logic for flights from Google Flight search result pages"""
    @property
    def flights(self) -> SelectorList:
        """Returns SelectorList for flights on given result page"""
        return self.xpath('//div[@jsaction="click:O1htCb;"]')

    def price(self, flight: Selector) -> Optional[str]:
        return flight.xpath('.//div[@class="YMlIz tu4g7b"]/span/text()').get()

    def operator(self, flight: Selector) -> Optional[str]:
        return flight.xpath('.//div[@class="TQqf0e sSHqwe tPgKwe ogfYpf"]/span/text()').get()

    def departure(self, flight: Selector, search_date: date) -> Optional[str]:
        departure_date = flight.xpath('.//g-bubble[1]').xpath('.//span[@class="eoY5cb"]/text()').get()
        return self._convert_date(departure_date, search_date)

    def arrival(self, flight: Selector, search_date: date) -> Optional[str]:
        arrival_date = flight.xpath('.//g-bubble[2]').xpath('.//span[@class="eoY5cb"]/text()').get()
        return self._convert_date(arrival_date, search_date)

    def _convert_date(self, flight_date: str, search_date: date) -> str:
        """Flight dates are in the form of '3:25 PM\xa0on\xa0Fri, Jan 1', so the correct year needs to be added."""
        fd = parse(flight_date)
        # Check if parsed date is before actual search date
        if fd.date() < search_date:
            # Check if flight_date is in January and search_date in December
            if fd.date().month == 1 and search_date.month == 12:
                # Add one year to flight_date for flights with duration from December to January
                fd = fd.replace(search_date.year + 1)
            else:
                # Set year to search_date's year if the flight is next year
                fd = fd.replace(search_date.year)
        return fd.isoformat()

    def duration(self, flight: Selector) -> Optional[str]:
        return flight.xpath('.//div[@class="gvkrdb AdWm1c tPgKwe ogfYpf"]/text()').get()

    def origin(self, flight: Selector) -> Optional[str]:
        return flight.xpath('(.//span[@jsname="d6wfac"])[3]/text()').get()

    def destination(self, flight: Selector) -> Optional[str]:
        return flight.xpath('(.//span[@jsname="d6wfac"])[4]/text()').get()

    def stops(self, flight: Selector) -> Optional[str]:
        return flight.xpath('.//span[@class="pIgMWd ogfYpf"]/@aria-label').get()

    def to_item(self, search_date: date):
        for flight in self.flights:
            yield {
                'price': self.price(flight),
                'operator': self.operator(flight),
                'departure': self.departure(flight, search_date),
                'arrival': self.arrival(flight, search_date),
                'duration': self.duration(flight),
                'origin': self.origin(flight),
                'destination': self.destination(flight),
                'stops': self.stops(flight)
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
    """Callback passed to PyppeteerMiddleware to load all flights before returning a response"""
    # JavaScript function to select and click button to show all flights 
    js_function = '''()=> {
        function getElementByXpath(path) {
            return document.evaluate(
                path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null
            ).singleNodeValue;
        }
        getElementByXpath('//div[@jsaction="click:yQf8Td"]').click();
    }'''
    try:
        await page.evaluate(js_function)
        # wait for 10 seconds to ensure that all flights are loaded
        await asyncio.sleep(10)
    except:
        # fails if no button found
        pass


class GoogleFlightsSpider(Spider):
    name = 'google_flights'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            PyppeteerMiddleware: 100,
            'scrapy_poet.InjectionMiddleware': 543,
        }
    }

    def __init__(self) -> None:
        f = pkgutil.get_data("scrapy_google_flights", "resources/searches.json")
        self.searches = json.loads(f)

    def start_requests(self) -> PyppeteerRequest:
        """Generate PyppeteerRequests for every search in self.searches"""
        for search in self.searches:
            url, search_date = self._get_flight_url(search)
            yield PyppeteerRequest(
                url,
                pyppeteer_callback=load_all_flights,
                cookies=consent_cookie,
                dont_filter=True,
                cb_kwargs={'search_date': search_date}
            )

    def _get_flight_url(self, flight_data: Dict[str, Union[str, int, None]]) -> Tuple[str, date]:
        """Create url for oneway flights from Dictionary"""
        origin = flight_data['origin']
        destination = flight_data['destination']
        departure_date_string, departure_date = self._get_date_for_url(flight_data['days_to_depart'])
        url = f'https://www.google.com/flights#flt={origin}.{destination}.{departure_date_string}' + ";tt:o"
        return url, departure_date

    def _get_date_for_url(self, days_until: int) -> Tuple[str, date]:
        """Create date as string in format YYYY-MM-DD.
        Adds number of days passed as parameter to today's date."""
        d = date.today() + timedelta(days=days_until)
        return f'{d.year}-{d.month:02d}-{d.day:02d}', d

    async def parse(self, response, page: FlightPage, search_date: date):
        return page.to_item(search_date)
