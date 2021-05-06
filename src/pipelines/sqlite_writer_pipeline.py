import sqlite3 as sqlite

import sys
import os
import mylogging as logging

class SQLiteWriterPipeline(object):
   
    def __init__(self):
        self.write_counter = 0
        self.write_chunks = 1000  # number of rows to write in one transaction

    def open_spider(self, spider):
        self.connection = sqlite.connect(os.path.join(sys.path[0],
                                                      "../data/ekatte_pop_1.sqlite"))
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS ekatte_pop ' +
                            '(id INTEGER PRIMARY KEY, ' +
                            'ekatte_str TEXT, ' +
                            'date TEXT, population INTEGER)')
        self.connection.commit()

    def close_spider(self, spider):
        if self.write_counter % self.write_chunks:
            # need to end the last transaction
            logging.debug(f'Writing chunk {self.write_counter}')
            self.cursor.execute('END TRANSACTION')
            self.connection.commit()

        self.connection.close()

    # Take the item and put it in database - do not allow duplicates
    def process_item(self, item, spider):

        insert_sql = ('insert into ekatte_pop (ekatte_str, date, population) '
                      'values (?, ?, ?)')

        if not self.write_counter % self.write_chunks:
            # new transaction
            self.cursor.execute('BEGIN TRANSACTION')

        self.cursor.execute(insert_sql,(item['ekatte_str'],
                                        item['date'],
                                        item['population']))

        self.write_counter = self.write_counter + 1
        
        if not self.write_counter % self.write_chunks:
            logging.info(f'Writing chunk {self.write_counter}')
            self.cursor.execute('END TRANSACTION')
            self.connection.commit()
        logging.info("Item stored")
        return item
