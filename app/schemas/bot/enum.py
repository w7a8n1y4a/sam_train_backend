import enum


class CommandNames(enum.Enum):
    """Команды поддерживаемые ботом"""

    PREDICT = 'predict'
    START = 'start'
    HELP = 'help'
