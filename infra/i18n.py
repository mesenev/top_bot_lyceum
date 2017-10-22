import contextlib
import locale


def setup_locale():
    with contextlib.suppress(locale.Error):
        locale.setlocale(locale.LC_TIME, "ru_RU")
