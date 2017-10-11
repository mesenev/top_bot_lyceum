import datetime
import logging
import pytz

CUPS_OF = 21
BOT_TOKEN = ''
LOGIN = ''
PASSWORD = ''
LOGIN_URL = ''
DATA_URL = ''
SESSION_ID = ''
NUMBER_OF_KIDS = 5
COOLDOWN_FOR_LIST = datetime.timedelta(hours=3)
TIMEZONE = pytz.timezone('Asia/Vladivostok')


def setup_logger(dispatcher):
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
                        filename='log')
    logger = logging.getLogger(__name__)

    # log all errors
    def error(bot, update, err):
        logger.warning('Update "%s" caused error "%s"' % (update, err))

    dispatcher.add_error_handler(error)


TITLES_LIST = [
    '👑 Бессменный лидер',
    '🥈 Неустанный преследователь',
    '🥉 Один из лучших',
    'Знает, что делает',
    'Хороший парень',
]

AFTERWORDS = [
    'Удачи ❤',
    'Этот список заговорён на удачу',
    'Похоже, кто-то хочет чай ☕',
    'Мои создатели выпили {} кружки чая ☕'.format(CUPS_OF),
]

NIGHTTIME_MESSAGES = [
    'Ночью доставка не работает. Добрых снов, добрый человек. 🚀',
    'Возвращайтесь на рассвете 🚀',
]

HEADERS = [
    'расклады следующие',
    'отметились',
    'зал славы',
]

COOLDOWN_MSGS = [
    'Терпение, друг',
    'Ещё рано',
    'Терпение, терпение',
]
PREPARE_MESSAGE =[
    "Давайте позвоним в яндекс",
    "Сейчас узнаем"
]

CONTRIBUTORS = [
    102660981,  # mesenev
]
