from functools import wraps
from time import sleep
from logger import log

log = log.getChild(__name__)


def backoff(start_sleep_time=0.1,
            factor=2,
            border_sleep_time=10,
            resourse_name=None):
    """
    Функция для повторного выполнения функции через некоторое время,
    если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor)
    до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    :param resource_name: имя ресурса для обращения
    """
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):

            attempt_count = 0
            t = start_sleep_time

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    log.info(f'Some problem occures with resource: {resourse_name}')
                    log.info('The problem is: ')
                    log.exception(e)
                    new_t = start_sleep_time * factor ** attempt_count
                    t = new_t if new_t < border_sleep_time else border_sleep_time
                    attempt_count += 1
                    log.info(f'Current attempt num is #{attempt_count + 1}')
                    log.info(f'Process will sleep about {t} sec...')
                    sleep(t)

        return inner
    return func_wrapper
