import asyncio

import pyppeteer
from scrapy.settings import Settings
from twisted.internet.defer import Deferred

from .http import PyppeteerRequest, PyppeteerResponse


class PyppeteerMiddleware:
    """Downloader Middleware to make requests through Pyppeteer"""
    def __init__(self, settings: Settings):
        # Check whether to start browser in headless mode or not
        headless = settings.get('PYPPETEER_HEADLESS', True)
        # Get event loop to instantiate pyppeteer browser before requests are processed
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._instantiate_browser(headless))

    async def _instantiate_browser(self, headless):
        """Create instance of pyppeteer browser"""
        self.browser = await pyppeteer.launch(headless=headless)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        if isinstance(request, PyppeteerRequest):
            return future_to_deferred(self.process_browser_request(request))

    async def process_browser_request(self, request: PyppeteerRequest):
        page = await self.browser.newPage()
        await page.setCookie(request.cookies)
        # go to url and wait until there are no network connections for 500 ms.
        goto_response = await page.goto(request.url, options={'waitUntil' : 'networkidle0'})
        if request.pyppeteer_callback:
            await request.pyppeteer_callback(page)
        response = await PyppeteerResponse.from_page(page, goto_response, request)
        await page.close()
        return response

def future_to_deferred(f):
    """Convert an asyncio Future to twisted Deferred.
    For more information see https://meejah.ca/blog/python3-twisted-and-asyncio"""
    return Deferred.fromFuture(asyncio.ensure_future(f))
