import logging


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
