# Scrapy settings for scrapy_google_flights project
BOT_NAME = 'scrapy_google_flights'
SPIDER_MODULES = ['scrapy_google_flights.spiders']
NEWSPIDER_MODULE = 'scrapy_google_flights.spiders'

ROBOTSTXT_OBEY = False

# set log levels for websockets and pyppeteer
import logging
logging.getLogger('websockets').setLevel(logging.WARNING)
logging.getLogger('pyppeteer').setLevel(logging.WARNING)
