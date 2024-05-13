import requests
from bs4 import BeautifulSoup
import re
import schedule
import time
from datetime import datetime
import telebot

today = datetime.now().strftime("%m/%d/%Y")
from kora_database import *
# Print the formatted date

bot_token = '1981790629:AAGXe9sBFiWWhzsUaeK-8ie7AhgRnYtKV_E'
bot = telebot.TeleBot(bot_token)


def send_message(message):
    bot.send_message('@test829435', message)


def get_request(match_type):
    res = requests.get(
        "https://www.yallakora.com/match-center/%D9%85%D8%B1%D9%83%D8%B2-%D8%A7%D9%84%D9%85%D8%A8%D8%A7%D8%B1%D9%8A%D8%A7%D8%AA?date={today}#days"
    )
    soup = BeautifulSoup(res.content, 'html.parser')
    # Find all div elements with class "item finish liItem"
    match_divs = soup.find_all('div', class_=f'item {match_type} liItem')
    return match_divs


def get_match_info(match_div, addata=None):
    # Extract team A data
    team_a = match_div.find('div', class_='teams teamA').find('p').text.strip()
    # Extract team B data
    team_b = match_div.find('div', class_='teams teamB').find('p').text.strip()
    # Extract match result data
    score_elems = match_div.find('div',
                                 class_='MResult').find_all('span',
                                                            class_='score')
    score_team_a = score_elems[0].text.strip()
    score_team_b = score_elems[1].text.strip()
    if addata == True:
        addData(f'{team_a},{team_b}', score_team_a, score_team_b)
    match_time = match_div.find('div', class_='MResult').find(
        'span', class_='time').text.strip()
    return f""" {team_a} Vs {team_b} \n النتيجة : {score_team_a}    -    {score_team_b} \n وقت المباراة : {match_time} \n"""


def chech_result():
    print('chech_result')
    match_divs = get_request('now')
    print(match_divs)
    for match_div in match_divs:
        print('loop')
        score_elems = match_div.find('div',
                                     class_='MResult').find_all('span',
                                                                class_='score')
        score_team_a = score_elems[0].text.strip()
        score_team_b = score_elems[1].text.strip()
        team_a = match_div.find('div',
                                class_='teams teamA').find('p').text.strip()
        team_b = match_div.find('div',
                                class_='teams teamB').find('p').text.strip()
        try:
            print('try GetData from Database')
            teamName = getData(f'{team_a},{team_b}')
            print(teamName)
        except:
            teamName = None
        if teamName:
            sql_score_team_a = teamName[2]
            sql_score_team_b = teamName[3]
            if sql_score_team_a == score_team_a and sql_score_team_b == score_team_b:
                print('true')
            else:
                send_message(
                    f'جوووووووووووووووووول \n {get_match_info(match_div),False}'
                )
                updateData(score_team_a, score_team_b, f'{team_a},{team_b}')
                #time.sleep(5)
        else:
            print('adding data')
            addData(f'{team_a},{team_b}', score_team_a, score_team_b)


def send_all_matches():
    delete()
    send_message('###### جدول مباريات اليوم ######')
    match_divs = get_request('future')
    for match_div in match_divs:
        print(get_match_info(match_div))
        send_message(get_match_info(match_div, True))


schedule.every().day.at('12:00').do(send_all_matches)
if __name__ == '__main__':
    while True:
        schedule.run_pending()
        chech_result()
        time.sleep(1)
        # print('waiting for next check')
