from urllib.request import Request, urlopen
import time
import concurrent.futures
import requests

links = open('wiki-links.txt', encoding='utf8').read().split('\n')


def links_checker(links_array):
    try:
        request = Request(
            links_array,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 9.0; Win65; x64; rv:97.0) Gecko/20105107 Firefox/92.0'},
        )
        resp = urlopen(request, timeout=5)
        code = resp.code
        resp.close()

        return code
    except Exception as e:
        return links_array, e


startTime = time.time()
if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for url in links:
            futures.append(executor.submit(links_checker, url))

        for future in concurrent.futures.as_completed(futures):
            try:
                print(future.result())
            except requests.HTTPError:
                print("ConnectTimeout.")

print("%s sec" % (time.time() - startTime))
