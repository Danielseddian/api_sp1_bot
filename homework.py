'''import logging
import os
import time
# from logging.handlers import RotatingFileHandler

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
# PATH = os.path.expanduser('~') + __name__ + '.log
RESPONSE_ERRORS = ['error', 'code']
VERDICTS = {'rejected': 'К сожалению в работе нашлись ошибки.',
            'reviewing': 'Работа взята на проверку',
            'approved': 'Ревьюеру всё понравилось, можно приступать '
                        'к следующему уроку.'}
CHECKED = 'Проверена работа "{homework_name}"!\n\n{verdict}'
UNKNOWN_STATUS = 'Неизвестный статус:\n\n{status}'


def make_logfile_path():
    root_path = os.path.expanduser('~')
    os.chdir(root_path)
    if not os.path.isdir('log_journal'):
        os.mkdir('log_journal')
    return root_path + '/log_journal/' + __name__ + '.log'


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    status = homework['status']
    verdict = VERDICTS[status]
    return CHECKED.format(homework_name=homework_name,
                          verdict=verdict)


def get_response(current_timestamp):
    data = {'from_date': current_timestamp}
    return requests.get(URL, params=data, headers=HEADERS).json()


def send_message(message, bot_client):
    return bot_client.send_message(CHAT_ID, message)


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOGGING_FORMAT,
        filename=make_logfile_path(),
        filemode='a'
    )
    current_timestamp = int(time.time()) - 2678400
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        new_homework = get_response(current_timestamp)
        if new_homework.get('homeworks'):
            send_message(parse_homework_status(
                new_homework.get('homeworks')[0]), bot_client
            )
        current_timestamp = new_homework.get('current_date',
                                             current_timestamp)
        time.sleep(300)'''
import logging
import os
import time
# from logging.handlers import RotatingFileHandler

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
# PATH = os.path.expanduser('~') + __name__ + '.log
RESPONSE_ERRORS = ['error', 'code']
VERDICTS = {'rejected': 'К сожалению в работе нашлись ошибки.',
            'reviewing': 'Работа взята на проверку',
            'approved': 'Ревьюеру всё понравилось, можно приступать '
                        'к следующему уроку.'}
CHECKED = 'Проверена работа "{homework_name}"!\n\n{verdict}'
UNKNOWN_STATUS = 'Неизвестный статус:\n\n{status}'
BOT_ERROR = 'Бот столкнулся с ошибкой: {exception}'
UNKNOWN_RESPONSE = 'Неожиданный ответ от сервера: {error}'


def make_logfile_path():
    root_path = os.path.expanduser('~')
    os.chdir(root_path)
    if not os.path.isdir('log_journal'):
        os.mkdir('log_journal')
    return root_path + '/log_journal/' + __name__ + '.log'


def parse_homework_status(homework):
    try:
        homework_name = homework['homework_name']
        status = homework['status']
        if status in VERDICTS:
            verdict = VERDICTS[status]
            return CHECKED.format(homework_name=homework_name,
                                  verdict=verdict)
        return UNKNOWN_STATUS.format(status=status)

    except Exception as exception:
        return BOT_ERROR.format(exception=exception)


def get_response(current_timestamp):
    data = {'from_date': current_timestamp}
    try:
        response = requests.get(URL, params=data, headers=HEADERS).json()
        for error in RESPONSE_ERRORS:
            if error in response:
                logging.error(UNKNOWN_RESPONSE.format(error=response[error]))
    except Exception as exception:
        response = exception
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
            new_homework = get_response(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot_client
                )
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(300)

        except Exception as exception:
            logger = logging.getLogger()
            logger.error(exception)
            try:
                send_message(BOT_ERROR.format(exception=exception), bot_client)
            except Exception as send_exception:
                if str(send_exception) != str(exception):
                    logger.error(send_exception)
            time.sleep(5)


if __name__ == '__main__':
    main()
    '''from unittest import TestCase, mock
    import unittest
    ReqEx = requests.RequestException           # Короткое имя для ожидаемого исключения

#   main()                                      # Старый вызов
    class TestReq(TestCase):                    # Часть трюка
        @mock.patch('requests.get')             # Указание, что будем подменять requests.get
        def test_raised(self, rq_get):          # Второй параметр - это подмена для requests.get
            rq_get.side_effect = mock.Mock(     # Главный трюк - настраиваем подмену, чтобы
                side_effect=ReqEx('testing'))   # бросалось это исключение
            main()                              # Все подготовили, запускаем
    unittest.main()
    from unittest import TestCase, mock
    JSON = {'error': 'testing'}
    class TestReq(TestCase):            # Часть трюка
        @mock.patch('requests.get')     # Указание, что будем подменять requests.get
        def test_error(self, rq_get):   # Второй параметр - это подмена для requests.get
            resp = mock.Mock()          # Главный трюк
            resp.json = mock.Mock(      #   настраиваем подмену, чтобы
                return_value=JSON)      #   при вызове .json() возвращался
            rq_get.return_value = resp  #   такой JSON
            main()                      # Все подготовили, запускаем
    unittest.main()
    JSON = {'homeworks': [{'homework_name': 'test', 'status': 'test'}]}
    JSON = {'homeworks': 1} (будет сбой на ...[0])'''
