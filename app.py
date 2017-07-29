import os
import requests
import smtplib
from datetime import datetime
import pytz
from email.message import EmailMessage
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

PROJECT_NAME = "WEATHER DISTRIBUTION"
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
TZ = os.getenv('TZ')
LEVEL_INFO = int(os.getenv('LEVEL_INFO', 1))
LOCAL_TZ = pytz.timezone(TZ)

sched = BlockingScheduler(timezone=pytz.timezone(TZ))


def get_celsium(temp_kelvin):
    return temp_kelvin - 273.15


def get_message(info):
    if info == "clear sky":
        return "you should have a walk this day"

    return "I recommend you to stay home and to do different useful things"


def get_localized_dt(utc_dt):
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(LOCAL_TZ)


def foo():
    data = {"lat": LATITUDE,
            "lon": LONGTITUDE,
            "APPID": APPID}

    resp = requests.get(URL, params=data)
    ret = resp.json()

    weather_items = ret['list'][:LEVEL_INFO]
    summary = '{city} weather summary\n'.format(city=ret["city"]["name"])

    for item in weather_items:
        temp = get_celsium(item["main"]["temp"])
        date = datetime.strptime(item["dt_txt"], '%Y-%m-%d %H:%M:%S')
        local_dt = get_localized_dt(date)
        time_format = local_dt.strftime('%H:%M o\'clock')
        weather_info = item["weather"][0]["description"]
        summary += '{time_format} : {temp:.1f} ({weather_info})\n'.format(
            weather_info=weather_info,
            time_format=time_format,
            temp=temp)

    smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtp.starttls()
    msg = EmailMessage()
    smtp.login(SENDER_EMAIL, PASSWORD)

    msg['Subject'] = PROJECT_NAME
    msg['From'] = SENDER_EMAIL
    msg['To'] = [SENDER_EMAIL]
    msg.set_content(summary)
    smtp.send_message(msg)
    smtp.quit()


@sched.scheduled_job(CronTrigger(hour=JOB_HOURS, minute=JOB_MINUTES))
def timed_job():
    foo()


sched.start()
