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
RESPONSE_ERRORS = ['error', 'code']
VERDICTS = {'rejected': 'К сожалению в работе нашлись ошибки.',
            'reviewing': 'Работа взята на проверку',
            'approved': 'Ревьюеру всё понравилось, можно приступать '
                        'к следующему уроку.'}
CHECKED = 'У вас проверили работу "{name}"!\n\n{verdict}'
UNKNOWN_STATUS = 'Неизвестный статус работы: {status}'
BOT_ERROR = 'Бот столкнулся с ошибкой: {exception}'
EXPECTED_FAILURE = 'Ожидаемые ошибки сервера: {error}'
CONNECTION_ERROR = ('Ошибка соединения: {exception} по адресу: {url} '
                    'с параметрами: {params}')
SEND_ERROR = 'Ошибка отправки сообщения'


def parse_homework_status(homework):
    name = homework['homework_name']
    status = homework['status']
    if status in VERDICTS:
        verdict = VERDICTS[status]
    else:
        raise ValueError(UNKNOWN_STATUS.format(status=status))
    return CHECKED.format(name=name, verdict=verdict)


def get_homework_statuses(current_timestamp):
    data = {'from_date': current_timestamp}
    try:
        response = requests.get(URL, params=data, headers=HEADERS)
    except Exception as exception:
        raise ConnectionError(
            CONNECTION_ERROR.format(exception=exception, url=URL,
                                    params=data))
    return response.json()


def send_message(message, bot_client):
    return bot_client.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            for error in RESPONSE_ERRORS:
                if new_homework[error]:
                    raise ValueError(EXPECTED_FAILURE.format(
                        error=new_homework[error]
                    ))
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot_client
                )
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(300)

        except Exception as exception:
            logging.error(BOT_ERROR.format(exception=exception), exc_info=True)
            try:
                send_message(BOT_ERROR.format(exception=exception), bot_client)
            except Exception:
                logging.error(SEND_ERROR, exc_info=True)
            time.sleep(5)


if __name__ == '__main__':
    LOGGING_FORMAT = '%(asctime)s, %(levelname)s, %(message)s, %(processName)s'
    HOME_PATH = os.path.expanduser('~')
    LOG_FOLDER = 'log_journal'


    def make_logfile_path():
        os.chdir(HOME_PATH)
        if not os.path.isdir(LOG_FOLDER):
            os.mkdir(LOG_FOLDER)
        return f'{HOME_PATH}/{LOG_FOLDER}/{__name__}.log'


    logging.basicConfig(
        level=logging.DEBUG,
        format=LOGGING_FORMAT,
        filename=make_logfile_path(),
        filemode='a'
    )

    main()
