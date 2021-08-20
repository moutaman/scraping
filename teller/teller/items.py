# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from dataclasses import dataclass

class TellerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class VehiclesPerson(scrapy.Item):
    phone = scrapy.Field()
    email = scrapy.Field()
    username = scrapy.Field()
    location = scrapy.Field()
    scraped_date = scrapy.Field()

class Urls(scrapy.Item):
    url = scrapy.Field()