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
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

# The following is a workaround to avoid dealing with BadGzipFile Exception
# while converting pyppeteer response headers to scrapy response headers.
# see: https://github.com/scrapy/scrapy/issues/2063
COMPRESSION_ENABLED = False


# -*- Spidermon settings -*-
# Enable Spidermon
SPIDERMON_ENABLED = True
EXTENSIONS = {
    'spidermon.contrib.scrapy.extensions.Spidermon': 500,
}
# MonitorSuite to be executed when spider starts
SPIDERMON_SPIDER_OPEN_MONITORS = {
    'scrapy_google_flights.monitors.SpiderOpenMonitorSuite',
}
# MonitorSuite to be executed when spider finishes
SPIDERMON_SPIDER_CLOSE_MONITORS = {
    'scrapy_google_flights.monitors.SpiderCloseMonitorSuite',
}
# The maximum of expected errors for ErrorCountMonitor
SPIDERMON_MAX_ERRORS = 0
# The minimum amount of expected items for ItemCountMonitor
SPIDERMON_MIN_ITEMS = 10
# Enable FieldCoverageMonitor
SPIDERMON_ADD_FIELD_COVERAGE = True
# This specifies how often values for a field should be found
SPIDERMON_FIELD_COVERAGE_RULES = {
    "dict/price": 0.8,  # 80%
    "dict/operator": 1.0,  # 100%
    "dict/departure": 1.0,  # 100%
    "dict/arrival": 1.0,  # 100%
    "dict/duration": 1.0,  # 100%
    "dict/origin": 1.0,  # 100%
    "dict/destination": 1.0,  # 100%
    "dict/stops": 1.0,  # 100%
}

# To receive messages via Telegram from this spider, set the following value to True
GOOGLE_FLIGHTS_ENABLE_TELEGRAM = False
# Set your Telegram api token here:
#SPIDERMON_TELEGRAM_SENDER_TOKEN = 'your token'
# Here you can set the recipients (chat id, group id or channel name):
#SPIDERMON_TELEGRAM_RECIPIENTS = ['chat id']

# Include notifications for positive monitoring outcomes
#SPIDERMON_TELEGRAM_NOTIFIER_INCLUDE_OK_MESSAGES = True
# Include notifications for negative monitoring outcomes
#SPIDERMON_TELEGRAM_NOTIFIER_INCLUDE_ERROR_MESSAGES = True
