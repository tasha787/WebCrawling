import scrapy
import pdb
import json
from berghausScraping.items import FatbraincrawlerItem
import re
from html import unescape

class FatbrainSpider(scrapy.Spider):
    name = "fatbrain_crawler"
    start_urls = ["https://www.fatbraintoys.com/toys/toy_categories/"]

    def parse(self, response):
        sub_categories = response.xpath("//div[@class = 'category-border']/parent::a/@href").extract()
        yield from response.follow_all(sub_categories, callback=self.parse_pagination)

    def parse_pagination(self, response):
          yield from self.parse_products(response)
          next_page_url = response.xpath("(//a[@title= 'Next']/@href)[1]").get()
          if next_page_url:
              yield response.follow(next_page_url, callback=self.parse_pagination)

    def parse_products(self, response):
        products = response.xpath("//h3[contains(@class,'product-catalog')]/parent::a/@href").extract()
        yield from response.follow_all(products, callback=self.parse_product_details)

    def parse_product_details(self, response):
        variant_data = response.xpath("(//script[@type='application/ld+json']/text())[2]").get()
        if variant_data:
            try:
                data = json.loads(variant_data)
                self.logger.info(f"Variant data loaded: {data}")
            except json.JSONDecodeError:
                self.logger.error(f"Failed to decode JSON from variant data: {variant_data}")
                return
        else:
            self.logger.warning("No variant data found")
            return

        description = response.xpath("(//div/h3[@id = 'description']/following::div/span/text())[1]").get()
        description = self.clean_text(description)

        if isinstance(data, dict):
            data = [data]

        for variant in data:
            if isinstance(variant, dict):
                offers_list = variant.get('offers', [])
                for offer in offers_list:
                    item = FatbraincrawlerItem()
                    item['has_variant'] = len(offers_list) > 1
                    item['product_url'] = f"{response.url}?ah={variant.get('sku', '')}"
                    item['name'] = variant.get('name', '')
                    item['sku'] = variant.get('sku', '')
                    item['mpn'] = variant.get('mpn', '')
                    item['availability'] = bool(offer.get('availability', ''))
                    item['price'] = float(offer.get('price', 0))
                    item['description'] = description
                    item['image_array'] = variant.get('image', '')
                    item['brand'] = variant.get('brand', {}).get('name', '')

                    image_url = response.xpath(f"//*[@sku='{variant.get('sku', '')}']/img/@src").get()
                    if not image_url:
                        image_url = variant.get('image', [''])[0]
                    item['image'] = image_url

                    item['barcode'] = variant.get('gtin12', '')
                    item['barcode_type'] = self.barcode_type(variant.get('gtin12', ''))
                    item['color'] = variant.get('color', '')
                    item['size'] = variant.get('size', '')

                    available_option_elements = response.xpath(f"//a[@sku='{variant.get('sku', '')}']/following::div[@class='col-xs-2 pt_hide']/span/text()").getall()
                    if available_option_elements:
                        available_option_text = available_option_elements.get()
                        item['available_option'] = f"{item['name']} {available_option_text}"
                    else:
                        item['available_option'] = item['name']

                    yield item
            else:
                self.logger.error(f"Unexpected variant format: {variant}")


    def clean_text(self, text):
        if text:
            text = unescape(text)
            text = re.sub(r'<.*?>', '', text)
            text = text.strip()
            text = re.sub(r'\s+', ' ', text)
        return text

    def barcode_type(self,string):
        length= len(string)
        if length == 13 or length == 8:
            return "EAN"
        elif  length == 12 or length == 11:
            return "UPC"
        elif length == 14:
            return "gtin"
