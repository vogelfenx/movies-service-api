from aioretry import RetryPolicyStrategy, RetryInfo


def retry_policy(info: RetryInfo,
                 start_sleep_time=0.1,
                 factor=2,
                 border_sleep_time=10,
                 ) -> RetryPolicyStrategy:
    """
    Функция политики рестарта.
    Использует наивный экспоненциальный рост времени повтора (factor)
    до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param info: класс aioretry.RetryInfo - требование пакета
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    """

    new_t = start_sleep_time * factor ** info.fails
    t = new_t if new_t < border_sleep_time else border_sleep_time

    return False, t
