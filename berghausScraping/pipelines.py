# # Define your item pipelines here
# #
# # Don't forget to add your pipeline to the ITEM_PIPELINES setting
# # See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# # useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


# class BerghausscrapingPipeline:
#     def process_item(self, item, spider):
#         return item


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import csv
from itemadapter import ItemAdapter
class BerghauscrawlPipeline:
    def open_spider(self, spider):
        self.csv_file = open('berghaus_crawl.csv', 'w', newline='')
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=[
            "product_url", "name", "sku", "mpn", "availability", "price", "description", "image", "image_array", "size", "color", "brand", "has_variant"
        ])
        self.csv_writer.writeheader()

    def close_spider(self, spider):
        self.csv_file.close()

    def process_item(self, item, spider):
        self.csv_writer.writerow(item)
        return item



class FatbraincrawlerPipeline:
    def open_spider(self, spider):
        self.csv_file = open('fatBrain_crawl.csv', 'w', newline='')
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=[
            "has_variant", "product_url", "name", "sku", "mpn", "availability", "price", "description", "image_array","brand", "image", "barcode", "barcode_type", "color", "size", "isPriceExcVAT", "available_option"
        ])
        self.csv_writer.writeheader()

    def close_spider(self, spider):
        self.csv_file.close()

    def process_item(self, item, spider):
        self.csv_writer.writerow(item)
        return item
