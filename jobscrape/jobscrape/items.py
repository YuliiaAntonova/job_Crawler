import scrapy


class GlassdoorJobItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    description = scrapy.Field()
    source = scrapy.Field()
    location = scrapy.Field()
    max_salary = scrapy.Field()
    min_salary = scrapy.Field()


class IndeedJobItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    description = scrapy.Field()
    source = scrapy.Field()
    location = scrapy.Field()
    min_salary = scrapy.Field()
    max_salary = scrapy.Field()
