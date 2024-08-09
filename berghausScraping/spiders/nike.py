import scrapy
import re
import pdb
import json


class NikeSpider(scrapy.Spider):
    name = "nike_crawler"
    start_urls = ["https://www.nike.com/"]
    seen_category_urls = set()

    def parse(self, response):
        category_urls = response.xpath('//header//a[@role="menuitem"]/@href').getall()
        print(category_urls)
        for url in category_urls:
            if url not in self.seen_category_urls:
                self.seen_category_urls.add(url)
                yield response.follow(url, callback=self.parse_category)

    def parse_category(self, response):
        conceptid = response.xpath("//meta[@name='branch:deeplink:$deeplink_path']/@content").re_first("conceptid=([\w-]+(?:,[\w-]+)*)")
        if conceptid:
            conceptid = conceptid.replace(',', '%2C')
            api_url = f'https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=C4E2BAEDB4E9F8B5CB49FE5588D01C43&country=us&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(US)%26filter%3Dlanguage(en)%26filter%3DemployeePrice(true)%26filter%3DattributeIds({conceptid})%26anchor%3D1%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=en&localizedRangeStr=%7BlowestPrice%7D%20%E2%80%94%20%7BhighestPrice%7D'
            yield scrapy.Request(api_url, callback=self.parse_products_pagination, meta={'anchor': 1})

    def parse_products_pagination(self, response):
        data = json.loads(response.text)
        products = data.get('data', {}).get('products', {}).get('products', [])
        for product in products:
            product_url = product.get('url', '').replace('{countryLang}', 'https://www.nike.com')
            yield response.follow(product_url,callback=self.product_description, meta={'product_url': product_url})

        next_page = data.get('data', {}).get('products', {}).get('pages', {}).get('next')
        if next_page:
            current_anchor = response.meta['anchor']
            next_anchor = current_anchor + 24
            next_url = response.url.replace(f'anchor%3D{current_anchor}', f'anchor%3D{next_anchor}')
            yield scrapy.Request(next_url, callback=self.parse_products_pagination, meta={'anchor': next_anchor})

    def product_description(self, response):
        # Implement the parsing logic for product details here
        pass


#     def _api_headers(self):
#         return {
#             'User-Agent': 'Scrapy/2.11.0 (+https://scrapy.org)',
#             'Accept': '*/*',
#             'Accept-Language': 'en-US,en;q=0.9',
#             'Connection': 'keep-alive',
#             'Referer': 'https://www.google.com/',
#             'Sec-Fetch-Dest': 'script',
#             'Sec-Fetch-Mode': 'no-cors',
#             'Sec-Fetch-Site': 'same-origin'
# }
