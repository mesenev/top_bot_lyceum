import logging
import logging.config
import os
import pprint
import site
import sys
import traceback

from telegram.parsemode import ParseMode

from config import LOG_CHAT_ID
from config.config_default import CONTRIBUTORS

excepthooks = []


def setup_logger():
    os.makedirs('logs', exist_ok=True)

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'tiny': {
                'tiny': '%(asctime)s: %(message)s'
            }
        },
        'handlers': {
            "console": {
                "class": "logging.StreamHandler",
                "level": "ERROR",
                "formatter": "standard",
                "stream": "ext://sys.stderr"
            },
            'default': {
                'level': 'INFO',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'standard',
                "filename": "logs/info.log",
                "encoding": "utf8",
                "when": 'D'
            },
            'error': {
                'level': 'ERROR',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'tiny',
                "filename": "logs/error.log",
                "encoding": "utf8",
                "when": 'D'
            },
        },
        'loggers': {
            '': {
                'handlers': ['console', 'default', 'error'],
                'level': 'INFO',
                'propagate': True
            }
        }
    })

    def on_except(ex_cls, ex, tb):
        logging.critical(''.join(traceback.format_tb(tb)))
        logging.critical("Uncaught exception",
                         exc_info=(ex_cls, ex, tb))

        for hook in excepthooks:
            hook(ex_cls, ex, tb)

    sys.excepthook = on_except


def setup_dispatcher_logging(dispatcher):
    logger = logging.getLogger(__name__)

    def is_site_module(filename: str):
        pkgs = site.getsitepackages()
        return any(filename.startswith(p) for p in pkgs)

    def format_tb(exc):
        tb = traceback.extract_tb(exc.__traceback__)
        for i in 0, -1:
            while tb and is_site_module(tb[i].filename):
                tb.pop(i)
        return ''.join(tb.format())

    def error(bot, update, err):
        ustr = pprint.pformat(update.to_dict(), width=120)
        logger.exception(f'Update: \n{ustr}')
        if update:
            qmsg = update.callback_query and update.callback_query.message
            message = update.mesage or qmsg
            if message:
                message.reply_text('Произошла какая-то ошибка. '
                                   'Мы уже работаем над этим...')
                if message.from_user.id in CONTRIBUTORS:
                    message.reply_text(f"```{format_tb(err)}{err}```",
                                       parse_mode=ParseMode.MARKDOWN)

    # This hooks telegram api-level errors
    dispatcher.add_error_handler(error)

    def on_except(ex_cls, ex, tb):
        bot = dispatcher.bot
        bot.send_message(chat_id=LOG_CHAT_ID,
                         text=''.join(traceback.format_tb(tb)) +
                              '{}: {}'.format(ex_cls, ex))

    excepthooks.append(on_except)
