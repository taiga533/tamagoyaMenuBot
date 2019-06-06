import boto3
import json
import logging
import urllib3
import os
import bs4
import re
import datetime
import random

logger = logging.getLogger()
logger.setLevel(logging.INFO)

JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')

def lambda_handler(event, context):
    response_message = get_today_menu()
    send_message(response_message)
    return "OK"
    
def send_message(message):
    send_api_url = os.environ["SLACK_CHANNEL_POST_URL"]
    http = urllib3.PoolManager()
    headers = {
        "Content-Type": "application/json; charset=UTF-8"
    }
    data = {
        "text": '<!here> ' + get_greeting_msg(),
        "attachments": [
            message
        ]
    }
    
    http.request('POST', send_api_url, body=json.dumps(data).encode("utf-8"), headers=headers)
    return

def get_today_weekday_number():
    time = datetime.datetime.now(JST)
    logger.info(time)
    return time.weekday()


def get_weekly_menu():
    weekly_menu_list = get_menu_init()

    weekly_menu_text = ""
    for daily_menu in weekly_menu_list:
        daily_menu_text = create_menu_string(daily_menu)
        if weekly_menu_text != "": weekly_menu_text += "\n"
        weekly_menu_text += daily_menu_text
    
    return weekly_menu_text

def get_today_menu():
    weekly_menu_list = get_menu_init()
    
    today_weekday_number = get_today_weekday_number()
    if today_weekday_number > 100:
        return "今日はお休みです"
    return create_menu_string(weekly_menu_list[today_weekday_number])
    
def get_menu_init():
    http = urllib3.PoolManager()
    weekly_menu_html = http.request('GET', 'http://www.tamagoya.co.jp/menu_list/')
    soup = bs4.BeautifulSoup(weekly_menu_html.data, 'html.parser')
    weekly_menu_wrapper = soup.find("div", id='weeklymenuList')
    weekly_menu_list = weekly_menu_wrapper.find_all("div", class_="item")
    return weekly_menu_list

def create_menu_string(daily_menu):
    day = daily_menu.find(class_="day").text
    menu_title = daily_menu.find(class_="title").text
    menu_content = daily_menu.find(class_="text").text
    menu_options = daily_menu.find(class_="option").text

    allergy_elemetns = daily_menu.find_all('li', class_="")
    allergy_text = ""
    if len(allergy_elemetns) == 0:
        allergy_text = "該当なし"

    for allergy_elemet in allergy_elemetns:
        if allergy_text != "": allergy_text += "\n"
        allergy_text += allergy_elemet.text
    
    return {
        "title": menu_title,
        "text": menu_content,
        "fields": [
            {
                "title": "その他情報",
                "value": menu_options
            },
            {
                "title": "アレルギー",
                "value": allergy_text
            }
        ]
    }
    
def get_greeting_msg():
    greeting_msgs = [
        "今日も元気に仕事ピヨ！今日のメニューはこれピヨ！",
        "みんなtavenalに移行しても、僕がいたことを忘れないで欲しいピヨ",
    ]
    return greeting_msgs[random.randint(0, len(greeting_msgs))]
