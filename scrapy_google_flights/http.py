from scrapy import Request
from scrapy.http import HtmlResponse

class PyppeteerRequest(Request):
    def __init__(self, *args, **kwargs):
        self.pyppeteer_callback = kwargs.pop('pyppeteer_callback', None)
        super().__init__(*args, **kwargs)

class PyppeteerResponse(HtmlResponse):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    # TODO set headers
    @classmethod
    async def from_page(cls, page, goto_response, request):
        return cls(
            page.url,
            status=goto_response.status,
            #headers=response.headers,
            body=await page.content(),
            encoding='utf-8',
            request=request
        )
