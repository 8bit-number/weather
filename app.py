import os
import requests
import smtplib
from datetime import datetime
import pytz
from email.message import EmailMessage
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

URL = os.getenv('URL')
APPID = os.getenv('APPID')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
PASSWORD = os.getenv('PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
LONGTITUDE = os.getenv('LONGTITUDE')
LATITUDE = os.getenv('LATITUDE')
JOB_HOURS = os.getenv('JOB_HOURS')
JOB_MINUTES = os.getenv('JOB_MINUTES')
TIMEZONE = os.getenv('TIMEZONE')


WEATHER_MSG = """
Hello, Stacy!
in {time_format} will be {temp:.0f} and {weather_info}
in {time_format} will be {temp:.0f} and {weather_info}
in {time_format} will be {temp:.0f} and {weather_info}
"""

sched = BlockingScheduler(timezone=pytz.timezone(TIMEZONE))


def get_celsium(temp_kelvin):
    return temp_kelvin - 273.15


def get_message(info):
    if info == "clear sky":
        return "you should have a walk this day"

    return "I recommend you to stay home and to do different useful things"


def foo():
    data = {"lat": LATITUDE,
            "lon": LONGTITUDE,
            "APPID": APPID}

    resp = requests.get(URL, params=data)
    ret = resp.json()

    weather_item = ret['list'][0:3]
    temp = get_celsium(weather_item["main"][0])
    date = datetime.strptime(weather_item["dt_txt"], '%Y-%m-%d %H:%M:%S')
    # dotm = date.strftime('%dth of %B')
    time_format = date.strftime('%H:%M o\'clock')
    weather_info = weather_item["weather"][0]["description"]

    # mesg = get_message(weather_info)
    body = WEATHER_MSG.format(weather_info=weather_info,
                              time_format=time_format,
                              temp=temp)

    smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtp.starttls()
    msg = EmailMessage()
    smtp.login(SENDER_EMAIL, PASSWORD)

    msg['Subject'] = "WEATHER DISTRIBUTION"
    msg['From'] = SENDER_EMAIL
    msg['To'] = [SENDER_EMAIL]
    msg.set_content(body)
    smtp.send_message(msg)
    smtp.quit()


@sched.scheduled_job(CronTrigger(hour=JOB_HOURS, minute=JOB_MINUTES))
def timed_job():
    foo()


sched.start()
