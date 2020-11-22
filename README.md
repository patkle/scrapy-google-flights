# scrapy-google-flights
This is a small project demonstrating how one could scrape flight data from Google Flights using scrapy and pyppeteer.
Currently only oneway flights are supported.

## requirements
To run this spider, you will need to install [pyppeteer](https://pypi.org/project/pyppeteer/), [scrapy-poet](https://pypi.org/project/scrapy-poet/) and [spidermon](https://pypi.org/project/spidermon/).

## starting the spider
After cloning and installing the necessary requirements, you should be able to start the spider with the command `scrapy crawl google_flights`. 
You can see more options for running the spider with `scrapy crawl --help`.

## changing the flight searches
The searches performed by the spider are performed in the file `searches.json`. This file can be found in the folder `scrapy_google_flights/resources/`.
The format looks like this:
```json
{
    "origin": "airport from which you start",
    "destination": "airport at which you arrive",
    "days_to_depart": days until start of flight
}
```

`origin` and `destination` are specified as [IATA airport codes](https://en.wikipedia.org/wiki/IATA_airport_code). `days_to_depart` is an integer which defines in how many days from now the flight starts.
For example, if you wanted to travel from "Berlin Brandenburg Airport" (BER) to "Barcelona–El Prat Airport" (BCN) in 30 days, your json would look like this:

```json
{
    "origin": "BER",
    "destination": "BCN",
    "days_to_depart": 30
}
```

## enable Spidermon notifications via Telegram
You can get notifications when the Spider starts and finishes via Telegram. 
To enable these notifications, you need to create a Telegram bot and obtain your api access token. 
A decent guide on how to do that can be found [here](https://www.siteguarding.com/en/how-to-get-telegram-bot-api-token).
After creating your bot, you can add and message it via Telegram. Then, you could replace <BOT_TOKEN_HERE> with your token and get the chat id here: `https://api.telegram.org/bot<BOT_TOKEN_HERE>/getUpdates`.

You can then set the following values in `settings.py`:
```python
SPIDERMON_TELEGRAM_SENDER_TOKEN = 'your api access token'
SPIDERMON_TELEGRAM_RECIPIENTS = ['chat id']
```

For more options see this guide: [How do I configure a Telegram bot for Spidermon?](https://spidermon.readthedocs.io/en/latest/howto/configuring-telegram-for-spidermon.html#steps)
