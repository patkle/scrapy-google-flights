# Scrapy settings for scrapy_google_flights project
BOT_NAME = 'scrapy_google_flights'
SPIDER_MODULES = ['scrapy_google_flights.spiders']
NEWSPIDER_MODULE = 'scrapy_google_flights.spiders'

# Set log levels for websockets and pyppeteer loggers.
# Logging here is very verboose, so better only set the levels lower if necessary.
import logging
logging.getLogger('websockets').setLevel(logging.WARNING)
logging.getLogger('pyppeteer').setLevel(logging.WARNING)

# Enable or disable headless mode for pyppeteer.
PYPPETEER_HEADLESS = False

# This is to avoid the add_reader() not implemented issue in asyncio.
# This can occur if you are running Python 3.8 on Windows.
# see: https://github.com/tornadoweb/tornado/issues/2751
import sys
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Enable AsyncioSelectorReactor to enable support for asyncio.
# This is an experimental feature in Scrapy.
# see: https://docs.scrapy.org/en/latest/topics/asyncio.html
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# The following is a workaround to avoid dealing with BadGzipFile Exception
# while converting pyppeteer response headers to scrapy response headers.
# see: https://github.com/scrapy/scrapy/issues/2063
COMPRESSION_ENABLED = False
