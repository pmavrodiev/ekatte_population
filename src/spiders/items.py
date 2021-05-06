from scrapy.item import Item, Field


class EkatteItem(Item):
    # DONE
    population = Field()  # a unique auto-generated ID for storing in DB
    
    date = Field()
    ekatte_str = Field()