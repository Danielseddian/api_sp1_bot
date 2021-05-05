import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
HEADERS = {'Authorization': 'OAuth ' + PRAKTIKUM_TOKEN}
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
LOGGING_FORMAT = '%(asctime)s, %(levelname)s, %(message)s, %(processName)s'
HOME_PATH = os.path.expanduser('~')
LOG_FOLDER = 'log_journal'
RESPONSE_ERRORS = ['error', 'code']
VERDICTS = {'rejected': 'К сожалению в работе нашлись ошибки.',
            'reviewing': 'Работа взята на проверку',
            'approved': 'Ревьюеру всё понравилось, можно приступать '
                        'к следующему уроку.'}
CHECKED = 'Проверена работа "{homework_name}"!\n\n{verdict}'
UNKNOWN_STATUS = 'Неизвестный статус:\n\n{status}'
BOT_ERROR = 'Бот столкнулся с ошибкой:\n\n{exception}'
UNKNOWN_RESPONSE = 'Неожиданный ответ от сервера: {error}'
CONNECTION_ERROR = 'Ошибка соединения:\n\n{exception}'
SEND_ERROR = 'Ошибка отправки сообщения'


def make_logfile_path():
    os.chdir(HOME_PATH)
    if not os.path.isdir(LOG_FOLDER):
        os.mkdir(LOG_FOLDER)
    return HOME_PATH + '/' + LOG_FOLDER + '/' + __name__ + '.log'


def parse_homework_status(homework):
    try:
        name = homework['homework_name']
        verdict = VERDICTS[homework['status']]

    except Exception as exception:
        raise ValueError(UNKNOWN_RESPONSE.format(exception=exception))
    return CHECKED.format(homework_name=homework['homework_name'],
                          verdict=VERDICTS[homework['status']])


def get_homework_statuses(current_timestamp):
    data = {'from_date': current_timestamp}
    try:
        response = requests.get(URL, params=data, headers=HEADERS).json()
        for error in RESPONSE_ERRORS:
            if error in response:
                raise ValueError(
                    UNKNOWN_RESPONSE.format(error=response[error])
                )
    except Exception as exception:
        raise ConnectionError(CONNECTION_ERROR.format(exception=exception))
    return response


def send_message(message, bot_client):
    return bot_client.send_message(CHAT_ID, message)


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOGGING_FORMAT,
        filename=make_logfile_path(),
        filemode='a'
    )
    current_timestamp = int(time.time())
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
            logging.error(exception)
            try:
                send_message(BOT_ERROR.format(exception=exception), bot_client)
            except Exception:
                raise ConnectionError(SEND_ERROR)
            time.sleep(5)


if __name__ == '__main__':
    main()
