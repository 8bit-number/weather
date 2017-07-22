#api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}
import os
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from email.message import EmailMessage


URL = os.getenv('URL')
APPID = os.getenv('APPID')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
PASSWORD = os.getenv('PASSWORD')

weather_msg = """
Hello, Stacy!
I'm your bot who will inform you about weather :)
For {dotm}, in {city} I could tell you, that in {time_format} will be {temp:.0f}°C
Tomorrow will be {weather_info}, so {mesg}
"""

def get_celsium(temp_kelvin):
    return temp_kelvin - 273.15


def foo():
    data = { "lat": input("enter latitude: "), 
             "lon": input("enter longitude: "), 
             "APPID": APPID}
    
    resp = requests.get(URL, params=data)
    ret = resp.json()

    temp = get_celsium(weather_item["main"]["temp"])
    date = datetime.strptime(weather_item["dt_txt"], '%Y-%m-%d %H:%M:%S')
    dotm = date.strftime('%dth of %B')
    time_format = date.strftime('%H:%M o\'clock')
    weather_info = weather_item["weather"][0]["description"]
    if weather_info == "clear sky":
        mesg = "you should have a walk this day"
    else:
        mesg = "I recommend you to stay home and to do different useful things"

    body = weather_msg.format(dotm=dotm, weather_info=weather_info, mesg=mesg, time_format=time_format, temp=temp, city=ret["city"]["name"])
    
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    msg = EmailMessage()
    smtp.login(SENDER_EMAIL, PASSWORD)

    msg['Subject'] = "WEATHER DISTRIBUTION"
    msg['From'] = SENDER_EMAIL
    msg['To'] = [SENDER_EMAIL]
    msg.set_content(body)
    smtp.send_message(msg)
    print('e-mail sent.')
    smtp.quit()

if __name__ == "__main__":
    foo()
