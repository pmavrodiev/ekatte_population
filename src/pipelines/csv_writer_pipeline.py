import sqlite3 as sqlite

import sys
import os
import mylogging as logging


class CsvWriterPipeline(object):
    # set up the logger
  
    def __init__(self):
        pass

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    # Take the item and put it in database - do not allow duplicates
    def process_item(self, item, spider):

        pass