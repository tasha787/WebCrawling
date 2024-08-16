# # Define here the models for your scraped items
# #
# # See documentation in:
# # https://docs.scrapy.org/en/latest/topics/items.html

# import scrapy


# class BerghausscrapingItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass


# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BerghauscrawlItem(scrapy.Item):
    product_url = scrapy.Field()
    name = scrapy.Field()
    sku = scrapy.Field()
    mpn = scrapy.Field()
    availability = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    image = scrapy.Field()
    image_array = scrapy.Field()
    size = scrapy.Field()
    color = scrapy.Field()
    brand = scrapy.Field()
    has_variant = scrapy.Field()
    barcode = scrapy.Field()
    barcode_type = scrapy.Field()
    isPriceExcVAT = scrapy.Field()


class FatbraincrawlerItem(scrapy.Item):
    has_variant = scrapy.Field()
    product_url = scrapy.Field()
    name = scrapy.Field()
    sku = scrapy.Field()
    mpn = scrapy.Field()
    availability = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    image_array = scrapy.Field()
    brand = scrapy.Field()
    image = scrapy.Field()
    barcode = scrapy.Field()
    barcode_type = scrapy.Field()
    color = scrapy.Field()
    size = scrapy.Field()
    isPriceExcVAT = scrapy.Field()
    hasVariant = scrapy.Field()
    available_option = scrapy.Field()


class ZatuGamesItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    sku = scrapy.Field()
    availability = scrapy.Field()
    image = scrapy.Field()
    images = scrapy.Field()
    description = scrapy.Field()
    barcode = scrapy.Field()
    barcode_type = scrapy.Field()
    mpn = scrapy.Field()
    size = scrapy.Field()
    color = scrapy.Field()
    isPriceExcVAT = scrapy.Field()
    has_variant = scrapy.Field()
