import logging
import logging.config
import os
import sys
import traceback

from config import LOG_CHAT_ID

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
        },
        'loggers': {
            '': {
                'handlers': ['console', 'default'],
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

    def error(bot, update, err):
        logger.warning('Update "%s" caused error "%s"' % (update, err))

    # This hooks telegram api-level errors
    dispatcher.add_error_handler(error)

    def on_except(ex_cls, ex, tb):
        bot = dispatcher.bot
        bot.send_message(chat_id=LOG_CHAT_ID,
                         text=''.join(traceback.format_tb(tb)) +
                              '{}: {}'.format(ex_cls, ex))

    excepthooks.append(on_except)
