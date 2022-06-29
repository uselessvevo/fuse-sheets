import enum


class SheetsLoggerEnum(enum.Enum):

    # Ошибка при обработке элемента массива
    ERROR = 'error'

    # Предупреждение
    WARNING = 'warning'

    # Информация
    INFO = 'info'
