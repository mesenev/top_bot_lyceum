from enum import Enum
from io import BytesIO
from itertools import zip_longest
from types import SimpleNamespace

import pygments.style
from PIL.ImageColor import getrgb
from pygments import highlight
from pygments.formatters import find_formatter_class
from pygments.formatters.img import FontNotFound
from pygments.lexers.python import PythonLexer
from pygments.styles import get_style_by_name
from telegram.callbackquery import CallbackQuery
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton as Button
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.message import Message
from telegram.parsemode import ParseMode
from telegram.update import Update

from config import CODE_FONT
from config import AVAILABLE_FONTS, AVAILABLE_SCHEMES
from methods import start


def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


class Style(SimpleNamespace):
    format = 'png'
    font = CODE_FONT
    color_scheme = 'default'
    show_text = True

    def __str__(self):
        fmt = ('Формат: {}\nШрифт: {}\nСхема: {}'
               '\nВыводить код текстом: {}')
        return fmt.format(self.format, self.font, self.color_scheme,
                          'да' if self.show_text else 'нет')


default_style = Style()

formats = 'html jpeg png svg'.split()


def hl_code(code, name, user_data):
    style: Style = user_data.get('style') or default_style

    formatter = find_formatter_class(style.format)

    css_style = ('pre.code{{ font-family: {}; }}'.format(style.font) +
                 'td.linenos{ '
                 'background-color: rgba(240, 240, 240, 0.11); }')

    scheme:pygments.style.Style = get_style_by_name(style.color_scheme)
    rgb = getrgb(scheme.background_color)[:3]
    lineno_bg = (*rgb, 20)

    highlighted = highlight(code,
                            PythonLexer(),
                            formatter(style=style.color_scheme,
                                      linenos = True,
                                      font_name=style.font,
                                      fontfamily=style.font,
                                      full=True,
                                      line_number_bg=lineno_bg,
                                      cssstyles=css_style))

    if style.format == 'html':
        highlighted = highlighted.replace(
            'background-color: #f0f0f0;',
            'background-color: rgba(240, 240, 240, 0.06);'
        )

    if isinstance(highlighted, str):
        highlighted = highlighted.encode()
    img = BytesIO(highlighted)
    img.name = 'code_{}.{}'.format(name, style.format)

    return img


class State(Enum):
    choice = 1


keyboard = [[Button(i, callback_data='style#{}#{}'.format(what, i))
             for i in lst]
            for what, lst in (('format', formats),
                              ('font', AVAILABLE_FONTS))]
keyboard += [[Button(i, callback_data='style#color_scheme#' + i) for i in l]
             for l in grouper(5, AVAILABLE_SCHEMES, '')]

ready_keyboard = [[Button('Готово', callback_data='style#ready#ready')],
                  [Button('Посмотреть, как получилось',
                          callback_data='style#ready#show')]]

keyboard += [[Button('Показывать текст', callback_data='style#text#')]]
keyboard += ready_keyboard

COVER = 'Потыкайте на кнопки ниже, а когда надоест, нажмите "Готово".\n'


def on_style(bot, update: Update, user_data):
    msg: Message = update.message

    user_data.setdefault('style', Style())
    msg.reply_text(COVER + str(user_data['style']),
                   reply_markup=InlineKeyboardMarkup(keyboard))

    return State.choice


def on_choose(bot, update: Update, user_data):
    query: CallbackQuery = update.callback_query
    msg: Message = query.message

    cmd, arg, name = query.data.split('#')
    if cmd != 'style':
        return

    style: Style = user_data['style']
    style_name = style.color_scheme + '_' + style.font.replace(' ', '_')

    next_state = State.choice

    if hasattr(style, arg):
        setattr(style, arg, name)
    elif arg == 'ready' and name == 'show':
        code = open('tests/test_python_code.testpy').read()
        try:
            msg.reply_document(hl_code(code, style_name, user_data))
        except FontNotFound:
            msg.reply_text('Вот это да! Шрифт не найден.'
                           '\nМожете сообщить разработчикам о проблеме.'
                           '\nА пока попробуйте другой шрифт.')
    elif arg == 'text':
        style.show_text = not style.show_text

    text = COVER + str(style)
    if arg == 'ready' and name == 'ready':
        next_state = ConversationHandler.END
        text = '<b>Настройки сохранены.</b>\n\n' + str(style)
        msg.delete()
        msg.reply_text(text, reply_markup=start.reply_markup,
                       parse_mode=ParseMode.HTML)
    elif msg.text != text:
        msg.edit_text(text,
                      reply_markup=InlineKeyboardMarkup(keyboard))
    return next_state


def on_fallback(bot, update: Update):
    msg: Message = update.message
    msg.reply_text('Вы всё ещё в диалоге настройки стиля. '
                   'Если вам надоело, щёлкните кнопку "Готово"',
                   reply_markup=InlineKeyboardMarkup(ready_keyboard))
    return State.choice


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('style', on_style, Filters.private,
                                 pass_user_data=True)],
    states={
        State.choice: [CallbackQueryHandler(on_choose,
                                            pass_user_data=True)],
    },
    fallbacks=[MessageHandler(Filters.all, on_fallback)]
)
