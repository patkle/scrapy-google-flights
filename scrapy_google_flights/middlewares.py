from pyppeteer import launch
from scrapy import signals
from scrapy.http import HtmlResponse
import asyncio

from .http import PyppeteerRequest

# TODO: fix concurrency & headers
class PyppeteerMiddleware:
    
    def __init__(self, settings):
        self.loop = asyncio.get_event_loop()
        #self.loop.run_until_complete(self._instantiate_browser())
    
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler.settings)
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware

    async def _instantiate_browser(self):
        self.browser = await launch(headless=False)

    async def _process_request(self, request, spider):
        if not isinstance(request, PyppeteerRequest):
            return
        #page = await self.browser.newPage()
        browser = await launch(headless=False)
        page = await browser.newPage()
        await page.setCookie(request.cookies)
        response = await page.goto(request.url, options={'waitUntil' : 'networkidle0'})
        if request.pyppeteer_callback:
            await request.pyppeteer_callback(page)
        content = await page.content()
        body = str.encode(content)
        response1 = HtmlResponse(
            page.url,
            status=response.status,
            #headers=response.headers,
            body=body,
            encoding='utf-8',
            request=request
        )
        await page.close()
        await browser.close()
        return response1
    
    def process_request(self, request, spider):
        result = self.loop.run_until_complete(self._process_request(request, spider))
        return result

    def spider_closed(self):
        """Close Pyppeteer browser when spider is closing"""
        self.loop.run_until_complete(self.browser.close())