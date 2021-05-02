import logging as lgg
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()
lgg.basicConfig(
    level=lgg.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(processName)s',
    filename='main.log',
    filemode='a'
)


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = ('Ревьюеру всё понравилось, можно приступать '
                   'к следующему уроку.')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    data = {'from_date': current_timestamp}
    headers = {'Authorization': 'OAuth ' + PRAKTIKUM_TOKEN}
    homework_statuses = requests.get(
        'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
        params=data, headers=headers
    )
    return homework_statuses.json()


def send_message(message, bot_client):
    logger = lgg.getLogger(__name__)
    logger.setLevel(lgg.INFO)
    handler = RotatingFileHandler('main.log', maxBytes=(5 * pow(10, 6)),
                                  backupCount=10)
    logger.addHandler(handler)
    return bot_client.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time()) - 2678400
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot_client
                )
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(300)

        except Exception as exception:
            send_message(f'Бот столкнулся с ошибкой: {exception}', bot_client)
            time.sleep(5)


if __name__ == '__main__':
    main()
