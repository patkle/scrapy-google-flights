# Scrapy settings for scrapy_google_flights project
BOT_NAME = 'scrapy_google_flights'
SPIDER_MODULES = ['scrapy_google_flights.spiders']
NEWSPIDER_MODULE = 'scrapy_google_flights.spiders'

ROBOTSTXT_OBEY = True

SELENIUM_HEADLESS = False
CHROME_DRIVER_PATH = None
