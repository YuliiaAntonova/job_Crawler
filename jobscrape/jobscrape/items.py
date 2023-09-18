# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GlassdoorJobItem(scrapy.Item):
    source = scrapy.Field()
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()
    min_salary = scrapy.Field()
    max_salary = scrapy.Field()
    rate_type = scrapy.Field()


class IndeedJobItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    min_salary = scrapy.Field()
    max_salary = scrapy.Field()
    salary_type = scrapy.Field()
    description = scrapy.Field()
    source = scrapy.Field()
    link = scrapy.Field()




