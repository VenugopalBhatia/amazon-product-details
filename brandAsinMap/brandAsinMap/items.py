# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item, Field
from scrapy.loader.processors import Compose, TakeFirst, Join, MapCompose
from w3lib.html import remove_tags

def clean(text):
    return text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ').strip()


class BrandasinmapItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    brand = scrapy.Field(output_processor=Compose(TakeFirst(), clean))
    title = scrapy.Field(output_processor=Compose(TakeFirst(), clean))
    asin = scrapy.Field(output_processor=Compose(TakeFirst(), clean))
    title = scrapy.Field(output_processor=Compose(TakeFirst(), clean))
    manufacturer = scrapy.Field(output_processor=TakeFirst())
    rating = scrapy.Field(output_processor=TakeFirst())
    rating_count = scrapy.Field(output_processor=TakeFirst())
    answered_questions = scrapy.Field(output_processor=Compose(TakeFirst(), clean))
    promote = scrapy.Field(output_processor=Compose(Join(), clean))
    mrp = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst())
    categories = scrapy.Field(output_processor=Compose(MapCompose(clean), lambda x: [txt for txt in x if txt]))
    fba = scrapy.Field(output_processor=TakeFirst())
    offers = scrapy.Field()
    extra_features = scrapy.Field(output_processor=Compose(Join(), clean))
    expiry_date = scrapy.Field(output_processor=Compose(Join(), clean))
    availability = scrapy.Field(output_processor=Compose(Join(), clean))
    merchant_info = scrapy.Field(output_processor=Compose(Join(), clean))
    olp = scrapy.Field(output_processor=Compose(Join(), clean))
    styles = scrapy.Field()
    design = scrapy.Field(output_processor=TakeFirst())
    features = scrapy.Field(output_processor=Compose(MapCompose(clean)))
    bsr = scrapy.Field(output_processor=Compose(Join(), clean))
    dfa = scrapy.Field(output_processor=Compose(Join(), clean))
    description = scrapy.Field(output_processor=Compose(Join(), clean))
    aplus_images = scrapy.Field()
    aplus_text = scrapy.Field(output_processor=Compose(MapCompose(clean), lambda x: [txt for txt in x if txt]))
    star_ratings = scrapy.Field(output_processor=TakeFirst())
    cr_summary = scrapy.Field(output_processor=TakeFirst())
    
    
    url = scrapy.Field(output_processor=TakeFirst())
   
    