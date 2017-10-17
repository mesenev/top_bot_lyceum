import logging
import logging.config
import os


def setup_logger(dispatcher):
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
                "encoding": "utf8"
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
