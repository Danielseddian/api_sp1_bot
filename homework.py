import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
ERROR_CODES = ['error', 'code']
VERDICTS = {'rejected': 'К сожалению в работе нашлись ошибки.',
            'reviewing': 'Работа взята на проверку',
            'approved': 'Ревьюеру всё понравилось, можно приступать '
                        'к следующему уроку.'}
CHECKED = 'У вас проверили работу "{name}"!\n\n{verdict}'
STATUS_ERROR = 'Неизвестный статус работы: {status}'
BOT_ERROR = 'Бот столкнулся с ошибкой: {error}'
RESPONSE_ERROR = ('Сервер: {URL} с параметрами: {params} и '
                  '{headers} вернул ошибку: {error}')
CONNECTION_ERROR = ('Ошибка соединения: {error} по адресу: {url} '
                    'с параметрами: {params} и {headers}')
SEND_ERROR = 'Ошибка отправки сообщения: {error}'


def get_homework_statuses(current_timestamp):
    data = dict(url=URL, params={'from_date': current_timestamp},
                headers=HEADERS)
    try:
        response = requests.get(**data)
    except requests.exceptions.RequestException as error:
        raise ConnectionError(CONNECTION_ERROR.format(
            error=error, **data))
    content = response.json()
    for error in ERROR_CODES:
        if error in content:
            raise ValueError(RESPONSE_ERROR.format(
                error=content[error], **data))
    return content


def parse_homework_status(homework):
    status = homework['status']
    if status not in VERDICTS:
        raise ValueError(STATUS_ERROR.format(status=status))
    return CHECKED.format(name=homework['homework_name'],
                          verdict=VERDICTS[status])


def send_message(message, bot_client):
    return bot_client.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    saved_error = None

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

        except Exception as error:
            error = BOT_ERROR.format(error=error)
            logging.error(error, exc_info=True)
            try:
                if saved_error != str(error):
                    saved_error = str(error)
                    send_message(error, bot_client)
            except Exception as send_exception:
                logging.error(SEND_ERROR.format(error=send_exception),
                              exc_info=True)
            time.sleep(5)


if __name__ == '__main__':
    LOGGING_FORMAT = '%(asctime)s, %(levelname)s, %(message)s, %(processName)s'
    LOG_FILE = f'{os.path.expanduser("~")}/log_journal/{__name__}.log'

    if not os.path.isdir(os.path.dirname(LOG_FILE)):
        os.mkdir(os.path.dirname(LOG_FILE))

    logging.basicConfig(
        level=logging.DEBUG,
        format=LOGGING_FORMAT,
        filename=LOG_FILE,
        filemode='a'
    )

    main()
