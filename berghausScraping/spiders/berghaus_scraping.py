import scrapy
import json
import re
from html import unescape
from berghausScraping.items import BerghauscrawlItem
from berghausScraping.utils import clean_text, barcode_type

class QuotesSpider(scrapy.Spider):
    name = "berghaus_crawler"
    start_urls = ["https://www.berghaus.com/"]

    def parse(self, response):
        try:
            categories = response.xpath("//a[@data-context='Shop All']/@href").extract()
            categories = list(dict.fromkeys(categories))
            yield from response.follow_all(categories, callback=self.parse_pagination)
        except Exception:
            print("Error occurred in parse function")

    def parse_pagination(self, response):
        try:
            yield from self.parse_products(response)
            next_page_url = response.xpath("(//a[contains(@class,'SelectorActive')]/following::a/@href)[1]").get()  # If there is a next page URL, follow it
            if next_page_url:
                yield response.follow(next_page_url, callback=self.parse_pagination)
        except Exception:
            print("Error occurred in parse_pagination function")

    def parse_products(self, response):
        try:
            products = response.xpath("(//a[@class='athenaProductBlock_linkImage']/@href)[position() mod 2 = 0]").extract()
            yield from response.follow_all(products, callback=self.parse_product_details)
        except Exception:
            print("Error occurred in parse_products function")
    def parse_product_details(self, response):
        try:
            variant_data = response.xpath("//script[@id='productSchema']/text()").get()
            if variant_data:
                try:
                    data = json.loads(variant_data)
                except json.JSONDecodeError:
                    print("Failed to decode JSON from variant data")
                    return

            description = response.xpath("(//div[@class='athenaProductPageSynopsisContent']/p/text())[1]").get()
            description = clean_text(description)
            image_array = response.xpath("//button[@type='button']/img/@src").extract()
            size = response.xpath("//span[@class = 'srf-hide']/parent::button/text()").get()
            color = response.xpath("//div[@aria-label='Colour']//select/option[@selected]/text()").get()
            size = clean_text(size)
            color = clean_text(color)
            brand = response.xpath("//div[@data-product-brand]/@data-product-brand").get()
            variants = data.get('hasVariant', []) if variant_data else []
            has_variant = len(variants) != 1

            for variant in variants:
                try:
                    item = BerghauscrawlItem()
                    item['product_url'] = self.format_url(response.url, variant.get('sku'))
                    item['name'] = variant.get('name')
                    item['sku'] = variant.get('sku')
                    item['mpn'] = variant.get('mpn')
                    availability_status = variant.get('offers', {}).get('availability', "")
                    item['availability'] = "InStock" in availability_status
                    item['price'] = float(variant.get('offers', {}).get('price'))
                    item['description'] = description
                    item['image'] = variant.get('image')
                    item['image_array'] = image_array
                    item['size'] = size
                    item['color'] = color
                    item['brand'] = brand
                    item['has_variant'] = bool(has_variant)
                    item['barcode'] = ""
                    item['barcode_type'] = ""
                    item['isPriceExcVAT'] = False

                    yield item
                except Exception:
                    print("Error occurred while processing variant")

        except Exception:
            print("Error occurred in parse_product_details function")

    def format_url(self, base_url, ssid):
        try:
            return f"{base_url}?variation={ssid}"
        except Exception:
            print("Error occurred in format_url function")
