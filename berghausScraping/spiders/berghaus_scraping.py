import scrapy
import json
import re
from html import unescape

from berghausScraping.items import BerghauscrawlItem

class QuotesSpider(scrapy.Spider):
    name = "berghaus_crawler"
    start_urls = ["https://www.berghaus.com/"]

    def parse(self, response):
        categories = response.xpath("//a[@data-context='Shop All']/@href").extract()
        categories = list(dict.fromkeys(categories))
        yield from response.follow_all(categories, callback=self.parse_pagination)

    def parse_pagination(self, response):
        yield from self.parse_products(response)
        next_page_url = response.xpath("(//a[contains(@class,'SelectorActive')]/following::a/@href)[1]").get()    # If there is a next page URL, follow it
        yield response.follow(next_page_url or '', callback=self.parse_pagination)

    def parse_products(self, response):
        products = response.xpath("(//a[@class='athenaProductBlock_linkImage']/@href)[position() mod 2 = 0]").extract()
        yield from response.follow_all(products, callback=self.parse_product_details)

    def parse_product_details(self, response):
        variant_data = response.xpath("//script[@id='productSchema']/text()").get()
        if variant_data:
         try:
            data = json.loads(variant_data)
         except json.JSONDecodeError:
            self.logger.error(f"Failed to decode JSON from variant data: {variant_data}")
            return
        description = response.xpath("(//div[@class='athenaProductPageSynopsisContent']/p/text())[1]").get()
        description = self.clean_text(description)
        image_array = response.xpath("//button[@type='button']/img/@src").extract()
        size = response.xpath("(//input[@data-selected]//following::button/text())[1]").get()
        color = response.xpath("//div[@aria-label='Colour']//select/option[@selected]/text()").get()
        size = self.clean_text(size)
        color = self.clean_text(color)
        brand = response.xpath("//div[@data-product-brand]/@data-product-brand").get()
        variants = data.get('hasVariant', [])
        has_variant = len(variants) != 1

        for variant in data.get('hasVariant', []):
            item = BerghauscrawlItem()
            item['product_url'] = self.format_url(response.url, variant.get('sku'))
            item['name'] = variant.get('name')
            item['sku'] = variant.get('sku')
            item['mpn'] = variant.get('mpn')
            item['availability'] = bool(variant.get('offers', {}).get('availability'))
            item['price'] = float(variant.get('offers', {}).get('price'))
            item['description'] = description
            item['image'] = variant.get('image')
            item['image_array'] = image_array
            item['size'] = size
            item['color'] = color
            item['brand'] = brand
            item['has_variant'] = bool(has_variant)
            yield item

    def format_url(self, base_url, ssid):
        return f"{base_url}?variation={ssid}"

    def clean_text(self, text):
        if text:
            text = unescape(text)
            text = re.sub(r'<.*?>', '', text)
            text = text.strip()
            text = re.sub(r'\s+', ' ', text)
        return text
