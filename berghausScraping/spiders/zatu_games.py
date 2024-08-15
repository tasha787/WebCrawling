import scrapy
import json
import csv
import re
import pdb
from html import unescape
from berghausScraping.items import FatbraincrawlerItem
from berghausScraping.utils import clean_text, barcode_type

class ZatuGamesSpider(scrapy.Spider):
    name = "zatu_games_crawler"
    start_urls = ["https://www.board-game.co.uk/"]
    seen_category_urls = set()

    def parse(self, response):
        try:
            category_urls = response.xpath("//div[@class='zgh-mega-menu-col zgh-one']/ul/li/a/@href").getall()
            print(category_urls)
            for url in category_urls:
                if url not in self.seen_category_urls:
                    self.seen_category_urls.add(url)
                    yield response.follow(url, callback=self.parse_pagination)
        except Exception:
            print("Error occurred in parse function")

    def parse_pagination(self, response):
        try:
            yield from self.parse_products(response)
            next_page_url = response.xpath("//span[text()='Next']/parent::a/@href").get()
            if next_page_url:
                yield response.follow(next_page_url, callback=self.parse_pagination)
        except Exception:
            print("Error occurred in parse_pagination function")

    def parse_products(self, response):
        try:
            products = response.xpath("//div[@class='zg-product-title']/h2/a/@href").extract()
            yield from response.follow_all(products, callback=self.parse_variants)
        except Exception:
            print("Error occurred in parse_products function")

    def parse_variants(self, response):
      yield from self.parse_product_details(response)
      variant = response.xpath("//ul[@id='vgs-switch-variations']/li/a/@href").getall()
      if variant:
        yield from response.follow_all(variant,callback= self.parse_product_details)

    def parse_product_details(self, response):
      try:
          url = response.url
          title = response.xpath("//h1[contains(@class,'product-title')]/text()").get()
          price = response.xpath("//div[contains(@class,'price-box-now')]/@data-now").get()
          sku = response.xpath("//span[@class='sku']/text()").get()
          availability_text = response.xpath("//span[@class='stock in-stock']/text()").get()
          availability = "IN STOCK" in (availability_text or "").upper()

          data = response.xpath("//script[@class='yoast-schema-graph']/text()").get()
          json_data = json.loads(data)
          image = json_data.get('@graph')[1].get('url')
          if not image:
              image = response.xpath("//div[@class='product-image-container']/img/@src").get()
          images = response.xpath("//div[contains(@class,'product-image-thumbs')]//@src").getall()
          description = response.xpath("//header[@class='perfect-products-static-header']/following-sibling::p//text()").getall()
          if not description:
              description = response.xpath("//div[@id='tab-description']//p//text()").getall()
          description = clean_text(' '.join(description))
          variant = response.xpath("//ul[@id='vgs-switch-variations']/li/a/@href").getall()
          has_variant = bool(variant)
          barcode = ""
          mpn = ""
          size = ""
          color = ""
          barcode_type = ""
          isPriceExcVAT = False

          yield {
              'url': url,
              'title': title,
              'price': price,
              'sku': sku,
              'availability': availability,
              'image': image,
              'images': images,
              'description': description,
              'barcode': barcode,
              'mpn': mpn,
              'size': size,
              'color': color,
              'barcode_type': barcode_type,
              'isPriceExcVAT': isPriceExcVAT,
              'has_variant': has_variant
          }

      except Exception:
          print("Error occurred in parse_product_details function")
