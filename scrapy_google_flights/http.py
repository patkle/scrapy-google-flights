from scrapy import Request
from scrapy.http import HtmlResponse

class PyppeteerRequest(Request):
    def __init__(self, *args, **kwargs):
        self.pyppeteer_callback = kwargs.pop('pyppeteer_callback', None)
        super().__init__(*args, **kwargs)

class PyppeteerResponse(HtmlResponse):
    pass
