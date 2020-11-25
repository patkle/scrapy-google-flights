from __future__ import annotations
from scrapy.http import HtmlResponse, Request
import pyppeteer


class PyppeteerRequest(Request):
    """Wrapper around Scrapy's Request to make requests using PyppeteerMiddleware"""
    
    def __init__(self, *args, **kwargs) -> None:
        # You can pass a function as callback which will be executed after the target
        # page is loaded. The callback will receive the page object as parameter.
        self.pyppeteer_callback = kwargs.pop('pyppeteer_callback', None)
        super().__init__(*args, **kwargs)


class PyppeteerResponse(HtmlResponse):
    """Wrapper around Scrapy's HtmlResponse which creates a response from 
    the objects provided by PyppeteerMiddleware"""
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @classmethod
    async def from_page(
        cls,
        page: pyppeteer.page.Page,
        response: pyppeteer.network_manager.Response,
        request: PyppeteerRequest
    ) -> PyppeteerResponse:
        return cls(
            page.url,
            status=response.status,
            headers=response.headers,
            body=await page.content(),
            encoding='utf-8',
            request=request
        )
