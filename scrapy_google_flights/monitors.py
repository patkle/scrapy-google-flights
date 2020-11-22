from spidermon import MonitorSuite
from spidermon.contrib.scrapy.monitors import ErrorCountMonitor
from spidermon.contrib.scrapy.monitors import FieldCoverageMonitor
from spidermon.contrib.scrapy.monitors import ItemCountMonitor
from spidermon.contrib.actions.telegram.notifiers import SendTelegramMessageSpiderStarted
from spidermon.contrib.actions.telegram.notifiers import SendTelegramMessageSpiderFinished


class TelegramMonitorSuite(MonitorSuite):
    """Monitor suite which checks if Telegram messages are enabled and, if yes,
    adds the provided Telegram message"""
    def __init__(self, message, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        telegram_enabled = self._crawler.settings.get('GOOGLE_FLIGHTS_ENABLE_TELEGRAM', False)
        if telegram_enabled:
            self.add_monitors_finished_action(message)


class SpiderOpenMonitorSuite(TelegramMonitorSuite):
    """Monitor suite which sends a Telegram message when the spider is started"""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(SendTelegramMessageSpiderStarted, *args, **kwargs)


class SpiderCloseMonitorSuite(TelegramMonitorSuite):
    """Monitor suite which sends a Telegram message when the spider stops"""
    monitors = [
        ItemCountMonitor,
        FieldCoverageMonitor,
        ErrorCountMonitor,
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(SendTelegramMessageSpiderFinished, *args, **kwargs)
