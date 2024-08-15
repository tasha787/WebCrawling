import scrapy
import json
import csv
import re
import pdb
from html import unescape
class ZatuGamesSpider(scrapy.Spider):
    name = "check"
    start_urls = ["https://www.board-game.co.uk/product/unmatched-ingen-vs-the-raptors/"]
    def parse(self, response):
      try:
          url = response.url
          title = response.xpath("//h1[contains(@class,'product-title')]/text()").get()
          price = response.xpath("//div[contains(@class,'price-box-now')]/@data-now").get()
          sku = response.xpath("//span[@class='sku']/text()").get()
          availability_text = response.xpath("//span[@class='stock in-stock']/text()").get()
          availability = "IN STOCK" in (availability_text or "").upper()
        #   pdb.set_trace()
          data = response.xpath("//script[@class='yoast-schema-graph']/text()").get()
          json_data = json.loads(data)
          image = json_data.get('@graph')[1].get('url')
          if not image:
              image = response.xpath("//div[@class='product-image-container']/img/@src").get()
          images = response.xpath("//div[contains(@class,'product-image-thumbs')]//@src").getall()
          description = response.xpath("//header[@class='perfect-products-static-header']/following-sibling::p//text()").getall()
          if not description:
              description = response.xpath("//div[@id='tab-description']//p//text()").getall()
          description = (' '.join(description))
          variant = response.xpath("//ul[@id='vgs-switch-variations']/li/a/@href").getall()
          has_variant = bool(variant)
          barcode = ""
          mpn = ""
          size = ""
          color = ""
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
              'isPriceExcVAT': isPriceExcVAT,
              'has_variant': has_variant
          }
      except Exception:
          print("Error occurred in parse_product_details function")
