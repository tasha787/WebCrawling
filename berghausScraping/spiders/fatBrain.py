# import scrapy
# import json
# import re
# from html import unescape
# from berghausScraping.items import FatbraincrawlerItem
# from berghausScraping.utils import clean_text, barcode_type

# class FatbrainSpider(scrapy.Spider):
#     name = "fat_brain_crawler"
#     start_urls = ["https://www.fatbraintoys.com/toys/toy_categories/"]

#     def parse(self, response):
#         sub_categories = response.xpath("//div[@class = 'category-border']/parent::a/@href").extract()
#         yield from response.follow_all(sub_categories,callback=self.parse_pagination)

#     def parse_pagination(self, response):
#         yield from self.parse_products(response)
#         next_page_url = response.xpath("(//a[@title= 'Next']/@href)[1]").get()
#         yield response.follow(next_page_url or '',callback=self.parse_pagination)

#     def parse_products(self, response):
#         products = response.xpath("//h3[contains(@class,'product-catalog')]/parent::a/@href").extract()
#         yield from response.follow_all(products,callback=self.parse_product_details)

#     def parse_product_details(self, response):
#         variant_data = response.xpath("//script[@type='application/ld+json'][contains(text(),'product')]/text()").get()
#         if variant_data:
#             try:
#                 data = json.loads(variant_data)
#                 self.logger.info(f"Variant data loaded: {data}")
#             except json.JSONDecodeError:
#                 self.logger.error(f"Failed to decode JSON from variant data: {variant_data}")
#                 return
#         else:
#             self.logger.warning("No variant data found")
#             return
#         description = response.xpath("(//div/h3[@id = 'description']/following::div/span/text())[1]").get()
#         description = clean_text(description)
#         if isinstance(data, dict):
#             data = [data]
#         for variant in data:
#             if isinstance(variant, dict):
#                 offers_list = variant.get('offers', [])
#                 for offer in offers_list:
#                     item = FatbraincrawlerItem()
#                     item['has_variant'] = len(offers_list) > 1
#                     item['product_url'] = f"{response.url}?ah={offer.get('sku', '')}"
#                     item['name'] = variant.get('name', '')
#                     item['sku'] = offer.get('sku', '')
#                     item['mpn'] = offer.get('mpn', '')
#                     item['availability'] = bool(offer.get('availability', ''))
#                     item['price'] = float(offer.get('price', 0))
#                     item['description'] = description
#                     item['image_array'] = variant.get('image', '')
#                     item['brand'] = variant.get('brand', {}).get('name', '')
#                     image_url = response.xpath(f"//*[@sku='{offer.get('sku', '')}']/img/@src").get()
#                     if not image_url:
#                         image_url = variant.get('image', [''])[0]
#                     item['image'] = image_url
#                     item['barcode'] = variant.get('gtin12', '')
#                     item['barcode_type'] = barcode_type(variant.get('gtin12', ''))
#                     item['color'] = offer.get('color', '')
#                     item['size'] = offer.get('size', '')
#                     item['isPriceExcVAT'] = False
#                     sku = offer.get('sku', '')
#                     available_option_elements = response.xpath(f"//span[@title='{sku}']/text()").getall()
#                     if available_option_elements:
#                         available_option_text = ' '.join(available_option_elements)
#                         item['available_option'] = f" {available_option_text}"
#                     else:
#                         item['available_option'] = item['name']
#                     yield item
#             else:
#                 self.logger.error(f"Unexpected variant format: {variant}")
import scrapy
import json
import re
from html import unescape
from berghausScraping.items import FatbraincrawlerItem
from berghausScraping.utils import clean_text, barcode_type

class FatbrainSpider(scrapy.Spider):
    name = "fat_brain_crawler"
    start_urls = ["https://www.fatbraintoys.com/toys/toy_categories/"]

    def parse(self, response):
        try:
            sub_categories = response.xpath("//div[@class = 'category-border']/parent::a/@href").extract()
            yield from response.follow_all(sub_categories, callback=self.parse_pagination)
        except Exception:
            print("Error occurred in parse function")

    def parse_pagination(self, response):
        try:
            yield from self.parse_products(response)
            next_page_url = response.xpath("(//a[@title= 'Next']/@href)[1]").get()
            if next_page_url:
                yield response.follow(next_page_url, callback=self.parse_pagination)
        except Exception:
            print("Error occurred in parse_pagination function")

    def parse_products(self, response):
        try:
            products = response.xpath("//h3[contains(@class,'product-catalog')]/parent::a/@href").extract()
            yield from response.follow_all(products, callback=self.parse_product_details)
        except Exception:
            print("Error occurred in parse_products function")

    def parse_product_details(self, response):
        try:
            variant_data = response.xpath("//script[@type='application/ld+json'][contains(text(),'product')]/text()").get()
            if variant_data:
                try:
                    data = json.loads(variant_data)
                    print("Variant data loaded")
                except json.JSONDecodeError:
                    print("Failed to decode JSON from variant data")
                    return
            else:
                print("No variant data found")
                return

            description = response.xpath("(//div/h3[@id = 'description']/following::div/span/text())[1]").get()
            description = clean_text(description)

            if isinstance(data, dict):
                data = [data]

            for variant in data:
                if isinstance(variant, dict):
                    offers_list = variant.get('offers', [])
                    for offer in offers_list:
                        item = FatbraincrawlerItem()
                        item['has_variant'] = len(offers_list) > 1
                        item['product_url'] = f"{response.url}?ah={offer.get('sku', '')}"
                        item['name'] = variant.get('name', '')
                        item['sku'] = offer.get('sku', '')
                        item['mpn'] = offer.get('mpn', '')
                        item['availability'] = bool(offer.get('availability', ''))
                        item['price'] = float(offer.get('price', 0))
                        item['description'] = description
                        item['image_array'] = variant.get('image', '')
                        item['brand'] = variant.get('brand', {}).get('name', '')

                        image_url = response.xpath(f"//*[@sku='{offer.get('sku', '')}']/img/@src").get()
                        if not image_url:
                            image_url = variant.get('image', [''])[0]
                        item['image'] = image_url

                        item['barcode'] = variant.get('gtin12', '')
                        item['barcode_type'] = barcode_type(variant.get('gtin12', ''))
                        item['color'] = offer.get('color', '')
                        item['size'] = offer.get('size', '')
                        item['isPriceExcVAT'] = False

                        sku = offer.get('sku', '')
                        available_option_elements = response.xpath(f"//span[@title='{sku}']/text()").getall()
                        if available_option_elements:
                            available_option_text = ' '.join(available_option_elements)
                            item['available_option'] = f" {available_option_text}"
                        else:
                            item['available_option'] = item['name']

                        yield item
                else:
                    print("Unexpected variant format")
        except Exception:
            print("Error occurred in parse_product_details function")
