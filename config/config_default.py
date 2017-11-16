import datetime
import pytz


#  OVERRIDE IT IN CONFIG.PY
BOT_TOKEN = ""
HOME_LINK = ""
P_URL = ""
LOGIN_URL = ""
LOG_CHAT_ID = ""
DATA_URL = ""
TAIL = ""

# LEAVE IT AS IS
CUPS_OF = 111
NUMBER_OF_KIDS = 5
COOLDOWN_FOR_LIST = datetime.timedelta(hours=3)
TIMEZONE = pytz.timezone('Asia/Vladivostok')
CODE_FONT = 'DejaVu Sans Mono'
AVAILABLE_FONTS = ['DejaVu Sans Mono']

AVAILABLE_SCHEMES = ['default', 'manni', 'perldoc', 'pastie', 'vs',
                     'fruity', 'monokai', 'paraiso-dark', ]


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
PREPARE_MESSAGE = [
    "Давайте позвоним туда",
    "Сейчас узнаем"
]

ANSWERS = [
    'Буддийская мудрость гласит: ответов всегда больше двух.',
    'Если достаточно долго думать, то обязательно получишь все ответы!',
    'Ответ ко всему один – усердная работа и труд.',
    'Будь настойчив! Я вот-вот выдам все ответы.',
    'https://youtu.be/WfA3tdG-_BA',
    '42',
    '[42, 42]',
    'http://bfy.tw/F30L',
    'Ваши страдания вызваны вашим сопротивлением тому, что есть.\n– Сиддхартха Гаутама',
    'Лучше есть хлеб со счастливым сердцем, чем обладать богатствами, терзаясь\n– Аменемопе',
    'Что толку в ответах, если они не получены самостоятельно?'
]

CONTRIBUTORS = [
    102660981,  # mesenev
    82204126,   # malyavin
]
