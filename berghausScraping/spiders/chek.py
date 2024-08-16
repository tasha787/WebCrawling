import scrapy
import json
import re
from html import unescape
from berghausScraping.items import BerghauscrawlItem
from berghausScraping.utils import clean_text, barcode_type

class QuotesSpider(scrapy.Spider):
    name = "check"
    start_urls = ["https://www.berghaus.com/women-s-linear-landscape-super-stretch-tee-red/13649742.html?variation=13649757"]

    def parse(self, response):
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
            size = clean_text(size)
            brand = response.xpath("//div[@data-product-brand]/@data-product-brand").get()
            availability_text = response.xpath("//span[contains(@class, 'stock')]/text()").get()
            availability = "In Stock" in (availability_text or "")

            variants = data.get('hasVariant', []) if variant_data else []
            has_variant = len(variants) != 1

            for variant in variants:
                try:
                    item = BerghauscrawlItem()
                    item['product_url'] = self.format_url(response.url, variant.get('sku'))
                    item['name'] = variant.get('name')
                    item['sku'] = variant.get('sku')
                    item['mpn'] = variant.get('mpn')
                    item['availability'] = availability
                    item['price'] = float(variant.get('offers', {}).get('price'))
                    item['description'] = description
                    item['image'] = variant.get('image')
                    item['image_array'] = image_array
                    item['size'] = size
                    item['brand'] = brand
                    item['has_variant'] = bool(has_variant)
                    item['barcode'] = ""
                    item['barcode_type'] = ""
                    item['isPriceExcVAT'] = False

                    # Extract color from name using regex
                    name = variant.get('name', '')
                    color_match = re.search(r'-(.*?) - \d+', name)
                    color = color_match.group(1).strip() if color_match else ""
                    item['color'] = clean_text(color)

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
