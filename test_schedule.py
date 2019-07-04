import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

app = Flask(__name__)


def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


scheduler = BackgroundScheduler()
scheduler.add_job(func=print_date_time, trigger="cron", hour=17, minute=10)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
if __name__ == "__main__":
    app.run()
