import random
import base64
import os
from scrapy import signals
from itemadapter import is_item, ItemAdapter
from random import choice
from berghausScraping.proxies import PROXIES, UK_PROXIES


class BerghausscrapingSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn't have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class BerghausscrapingDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        # s.retry_times = crawler.settings.getint('RETRY_TIMES', 20)
        # s.retry_http_codes = set(crawler.settings.getlist('RETRY_HTTP_CODES', [403, 500, 502, 503, 504, 572]))
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        if response.status in self.retry_http_codes:
            reason = f"HTTP status code {response.status}"
            return self._retry(request, reason, spider)
        return response

    def process_exception(self, request, exception, spider):
        return self._retry(request, exception, spider)

    # def _retry(self, request, reason, spider):
    #     retries = request.meta.get('retry_times', 0) + 1
    #     if retries <= self.retry_times:
    #         spider.logger.info(f"Retrying {request.url} (failed {retries} times)")
    #         request.meta['retry_times'] = retries
    #         return request
    #     else:
    #         spider.logger.error(f"Gave up retrying {request.url} (failed {retries} times)")
    #         return None

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

# class ProxyMiddleware:
#     def __init__(self):
#         self.proxies = PROXIES

#     def get_random_proxy(self):
#         return choice(self.proxies)

#     def process_request(self, request, spider):
#         proxy = self.get_random_proxy()
#         proxy_str = f"http://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
#         request.meta['proxy'] = proxy_str
#         print(request.meta['proxy'])


# class RandomUserAgentMiddleware:
#     def __init__(self):
#         self.user_agents = self.load_user_agents()

#     def load_user_agents(self):
#         file_path = os.path.join(os.path.dirname(__file__), 'user_agents.txt')
#         with open(file_path, 'r') as f:
#             return [line.strip() for line in f if line.strip()]

#     def process_request(self, request, spider):
#         request.headers['User-Agent'] = random.choice(self.user_agents)




# import random
# import os
# from scrapy import signals
# from itemadapter import is_item, ItemAdapter
# from random import choice
# from berghausScraping.proxies import PROXIES, UK_PROXIES

# class BerghausscrapingSpiderMiddleware:
#     @classmethod
#     def from_crawler(cls, crawler):
#         s = cls()
#         crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#         return s

#     def process_spider_input(self, response, spider):
#         return None

#     def process_spider_output(self, response, result, spider):
#         for i in result:
#             yield i

#     def process_spider_exception(self, response, exception, spider):
#         pass

#     def process_start_requests(self, start_requests, spider):
#         for r in start_requests:
#             yield r

#     def spider_opened(self, spider):
#         spider.logger.info('Spider opened: %s' % spider.name)


# class BerghausscrapingDownloaderMiddleware:
#     @classmethod
#     def from_crawler(cls, crawler):
#         s = cls()
#         crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#         s.retry_times = crawler.settings.getint('RETRY_TIMES', 20)
#         s.retry_http_codes = set(crawler.settings.getlist('RETRY_HTTP_CODES', [403, 500, 502, 503, 504, 572]))
#         return s

#     def process_request(self, request, spider):
#         return None

#     def process_response(self, request, response, spider):
#         if response.status in self.retry_http_codes:
#             reason = f"HTTP status code {response.status}"
#             return self._retry(request, reason, spider)
#         return response

#     def process_exception(self, request, exception, spider):
#         return self._retry(request, exception, spider)

#     def _retry(self, request, reason, spider):
#         retries = request.meta.get('retry_times', 0) + 1
#         if retries <= self.retry_times:
#             spider.logger.info(f"Retrying {request.url} (failed {retries} times)")
#             request.meta['retry_times'] = retries
#             return request
#         else:
#             spider.logger.error(f"Gave up retrying {request.url} (failed {retries} times)")
#             return None

#     def spider_opened(self, spider):
#         spider.logger.info('Spider opened: %s' % spider.name)


# class ProxyMiddleware:
#     def __init__(self):
#         self.proxies = PROXIES

#     def get_random_proxy(self):
#         return choice(self.proxies)

#     def process_request(self, request, spider):
#         proxy = self.get_random_proxy()
#         proxy_str = f"http://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
#         request.meta['proxy'] = proxy_str
#         spider.logger.info(f"Using proxy: {request.meta['proxy']}")  # Added logging


# class RandomUserAgentMiddleware:
#     def __init__(self):
#         self.user_agents = self.load_user_agents()

#     def load_user_agents(self):
#         file_path = os.path.join(os.path.dirname(__file__), 'user_agents.txt')
#         with open(file_path, 'r') as f:
#             return [line.strip() for line in f if line.strip()]

#     def process_request(self, request, spider):
#         user_agent = random.choice(self.user_agents)
#         request.headers['User-Agent'] = user_agent
#         spider.logger.info(f"Using User-Agent: {user_agent}")  # Added logging


# class CustomHeadersMiddleware:
#     def __init__(self):
#         self.custom_headers = {
#             'Accept-Language': 'en-US,en;q=0.9',
#             'Accept-Encoding': 'gzip, deflate, br',
#             'Connection': 'keep-alive',
#             'Upgrade-Insecure-Requests': '1'
#         }

#     def process_request(self, request, spider):
#         for header, value in self.custom_headers.items():
#             request.headers.setdefault(header, value)
#         spider.logger.info(f"Using headers: {self.custom_headers}")  # Added logging
