from __future__ import annotations
import asyncio
from typing import Coroutine

import pyppeteer
from scrapy.settings import Settings
from scrapy.spiders import Spider
from scrapy.crawler import Crawler
from scrapy.utils.reactor import verify_installed_reactor
from twisted.internet.defer import Deferred

from .http import PyppeteerRequest, PyppeteerResponse


class PyppeteerMiddleware:
    """Downloader Middleware to make requests through Pyppeteer"""
    def __init__(self, settings: Settings) -> None:
        # Check if AsyncioSelectorReactor is installed
        # If this is not the case, an exception is thrown
        verify_installed_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")
        # Check whether to start browser in headless mode or not
        headless = settings.get('PYPPETEER_HEADLESS', True)
        # Get event loop to instantiate pyppeteer browser before requests are processed
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._instantiate_browser(headless))

    async def _instantiate_browser(self, headless: bool) -> None:
        """Create instance of pyppeteer browser"""
        self.browser = await pyppeteer.launch(headless=headless)

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> PyppeteerMiddleware:
        return cls(crawler.settings)

    def process_request(self, request: PyppeteerRequest, spider: Spider) -> Deferred:
        # process request only if it is of type PyppeteerRequest
        if isinstance(request, PyppeteerRequest):
            return coroutine_to_deferred(self.process_browser_request(request))

    async def process_browser_request(self, request: PyppeteerRequest) -> PyppeteerResponse:
        page = await self.browser.newPage()
        await page.setCookie(request.cookies)
        # go to url and wait until there are no network connections for 500 ms.
        goto_response = await page.goto(request.url, options={'waitUntil': 'networkidle0'})
        if request.pyppeteer_callback:
            await request.pyppeteer_callback(page)
        response = await PyppeteerResponse.from_page(page, goto_response, request)
        await page.close()
        return response


def coroutine_to_deferred(c: Coroutine) -> Deferred:
    """Convert a coroutine to twisted Deferred."""
    # see: https://twistedmatrix.com/trac/ticket/8748
    # convert Coroutine to asyncio.Future
    future = asyncio.ensure_future(c)
    # convert asyncio.Future to Deferred
    return Deferred.fromFuture(future)
