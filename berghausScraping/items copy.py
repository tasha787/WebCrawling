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
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass



# class BerghausItem(scrapy.Item):
#     product_url = scrapy.Field()
#     name = scrapy.Field()
#     sku = scrapy.Field()
#     mpn = scrapy.Field()
#     availability = scrapy.Field()
#     price = scrapy.Field()
#     description = scrapy.Field()
#     image = scrapy.Field()
#     image_array = scrapy.Field()
