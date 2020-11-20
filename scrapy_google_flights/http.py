from __future__ import annotations
from scrapy import Request
from scrapy.http import HtmlResponse
import pyppeteer


class PyppeteerRequest(Request):
    def __init__(self, *args, **kwargs) -> None:
        self.pyppeteer_callback = kwargs.pop('pyppeteer_callback', None)
        super().__init__(*args, **kwargs)


class PyppeteerResponse(HtmlResponse):
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
