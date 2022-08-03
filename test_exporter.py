from prometheus_client import start_http_server, Counter
import pycurl
import time
import threading
from io import BytesIO
# Создание типа данных счетчика prometheus из client_python
url_http_code = Counter("url_http_code", "request http_code of the host",['code','url'])
url_http_request_time = Counter("url_http_request_time", "request http_request_time of the host",['le','url'])
http_request_total = Counter("http_request_total", "request request total of the host",['url'])
#curl url, код статуса возврата и общее время
def test_website(url):
    buffer_curl = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.WRITEDATA, buffer_curl)
    curl.setopt(curl.CONNECTTIMEOUT, 3)
    curl.setopt(curl.TIMEOUT, 3)
    try:
        curl.perform()
    except pycurl.error:
        http_code = 500
        http_total_time = 999
    else:
        http_code = curl.getinfo(pycurl.HTTP_CODE)
        http_total_time = curl.getinfo(pycurl.TOTAL_TIME)
    return http_code, http_total_time
# В соответствии с возвращаемым значением curl, подсчитать данные, отображаемые экспортером
def count_metric(url):
    http_code, http_total_time = test_website(url)
    if http_code >= 100 and http_code < 200 :
        url_http_code.labels('1xx',url).inc()
    elif http_code >= 200 and http_code < 300 :
        url_http_code.labels('2xx',url).inc()
    elif http_code >= 300 and http_code < 400 :
        url_http_code.labels('3xx',url).inc()
    elif http_code >= 400 and http_code < 500 :
        url_http_code.labels('4xx',url).inc()
    else:
        url_http_code.labels('5xx',url).inc()
    if http_total_time < 1 :
        url_http_request_time.labels('1',url).inc()
    elif http_total_time < 2 :
        url_http_request_time.labels('2',url).inc()
    elif http_total_time < 3 :
        url_http_request_time.labels('3',url).inc()
    else :
        url_http_request_time.labels('+Inf',url).inc()
    http_request_total.labels(url).inc()
# Управление потоком, выполнять curl url каждые 5 секунд
def count_threads(url):
    while True:
        t = threading.Thread(target=count_metric,args=(url,))
        t.setDaemon(True)
        t.start()
        time.sleep(15)
# Запустить процесс для каждого доменного имени, которое необходимо отслеживать
if __name__ == '__main__':
    start_http_server(9091)
    server_list = [
            'www.baidu.com',
            'www.qq.com',
            'blog.csdn.net',
            'github.com',
            'google.com',
            'www.ru'
            ]
    threads = []
    for url in server_list:
        t = threading.Thread(target=count_threads,args=(url,))
        threads.append(t)
    for thread in threads:
        thread.setDaemon(True)
        thread.start()
    thread.join()
