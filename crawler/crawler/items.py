# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class Dormitory(scrapy.Item):
    date = scrapy.Field()
    time = scrapy.Field()
    location = scrapy.Field()
    menu = scrapy.Field()

class Student(scrapy.Item):
    date = scrapy.Field()
    time = scrapy.Field()
    location = scrapy.Field()
    menu = scrapy.Field()
