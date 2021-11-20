# Параллелизм и асинхронность

Мы затронем только самые общие аспекты работы с потоками и процессами. Задачи, которые мы будем рассматривать обладают свойством [чрезвычайная параллельности](https://ru.wikipedia.org/wiki/%D0%A7%D1%80%D0%B5%D0%B7%D0%B2%D1%8B%D1%87%D0%B0%D0%B9%D0%BD%D0%B0%D1%8F_%D0%BF%D0%B0%D1%80%D0%B0%D0%BB%D0%BB%D0%B5%D0%BB%D1%8C%D0%BD%D0%BE%D1%81%D1%82%D1%8C).

Образцом для работы мы примем два куска кода из примера документации CPython для модуля [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html). Класc, больше подходящий для IO-bound задач: `ThreadPoolExecutor` (используются потоки), а для CPU-bound &mdash; `ProcessPoolExecutor` (используются процессы). Оба работают по принципу запуска одноранговых воркеров с некоторой функцией внутри (как кассы в &laquo;Пятерочке&raquo;).

## ThreadPoolExecutor

```python
import concurrent.futures
import urllib.request

URLS = ['http://www.foxnews.com/',
        'http://www.cnn.com/',
        'http://europe.wsj.com/',
        'http://www.bbc.co.uk/',
        'http://some-made-up-domain.com/']

# Retrieve a single page and report the URL and contents
def load_url(url, timeout):
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        return conn.read()

# We can use a with statement to ensure threads are cleaned up promptly
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Start the load operations and mark each future with its URL
    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
        else:
            print('%r page is %d bytes' % (url, len(data)))
```
## ProcessPoolExecutor

```python
import concurrent.futures
import math

PRIMES = [
    112272535095293,
    112582705942171,
    112272535095293,
    115280095190773,
    115797848077099,
    1099726899285419]

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True

def main():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for number, prime in zip(PRIMES, executor.map(is_prime, PRIMES)):
            print('%d is prime: %s' % (number, prime))

if __name__ == '__main__':
    main()
```

Возврат в синхронный код происходит благодаря использованию генератора `concurrent.futures.as_completed`, который возвращает результаты по мере готовности их в воркерах. Ручная синхронизация отсутствует, что очень удобно.
