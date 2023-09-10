import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


class SchedulerHandler:
    def __init__(self, morning_callback: callable):
        self.scheduler = AsyncIOScheduler()

        self.morning_callback = morning_callback

    def start(self):
        self.scheduler.add_job(
            self.morning_callback,
            CronTrigger(hour=8, minute=0, timezone=pytz.timezone('Europe/Warsaw'))
        )
        self.scheduler.start()
