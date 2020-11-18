from scrapy import Request
from scrapy.http import HtmlResponse

class SeleniumRequest(Request):
    def __init__(self, *args, **kwargs):
        self.selenium_callback = kwargs.pop('selenium_callback', None)
        self.selenium_cb_kwargs = kwargs.pop('selenium_cb_kwargs', None)
        super().__init__(*args, **kwargs)
        
class SeleniumResponse(HtmlResponse):
    @classmethod
    def from_driver(cls, driver, request):
        return cls(
            driver.current_url,
            body=str.encode(driver.page_source),
            encoding='utf-8',
            request=request
        )
