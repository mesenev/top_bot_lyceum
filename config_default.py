import datetime
import logging
import pytz

CUPS_OF = 21
BOT_TOKEN = ''
LOGIN = ''
PASSWORD = ''
LOGIN_URL = 'https://lms.yandexlyceum.ru/accounts/login/'
DATA_URL = ''
SESSION_ID = ''
NUMBER_OF_KIDS = 5
COOLDOWN_FOR_LIST = datetime.timedelta(hours=3)
TIMEZONE = pytz.timezone('Asia/Vladivostok')


def setup_logger(dispatcher):
    logfmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=logfmt, level=logging.INFO,
                        filename='log')
    logger = logging.getLogger(__name__)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    logging.getLogger('').addHandler(ch)

    # log all errors
    def error(bot, update, err):
        logger.warning('Update "%s" caused error "%s"' % (update, err))

    dispatcher.add_error_handler(error)


CONTRIBUTORS = [
    102660981,  # mesenev
]
