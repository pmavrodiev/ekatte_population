import sqlite3 as sqlite

import sys
import os
import logging

from src.simple_logging.custom_logging import setup_custom_logger


class SQLiteWriterPipeline(object):
    # set up the logger
    LOGGING_LEVEL = logging.INFO
    logger = setup_custom_logger('SQLiteWriterPipeline', LOGGING_LEVEL,
                                 flog=os.path.join(sys.path[0],
                                                   "../logs/pipeline_mongodbwriter.log"))

    def __init__(self):
        self.write_counter = 0
        self.write_chunks = 100  # number of rows to write in one transaction

    def open_spider(self, spider):
        self.connection = sqlite.connect(os.path.join(sys.path[0],
                                                      "../data/jobsch.sqlite"))
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS jobsch ' +
                            '(id INTEGER PRIMARY KEY, ' +
                            'unique_id TEXT, ' +
                            'url TEXT, ' +
                            'posting_id TEXT, ' +
                            'date_parsed TEXT, ' +
                            'date_published TEXT, ' +
                            'source TEXT, ' +
                            'job_title TEXT, ' +
                            'location TEXT, ' +
                            'occupation TEXT, ' +
                            'job_rank TEXT, ' +
                            'company_name TEXT, ' +
                            'raw_content BLOB, ' +
                            'parsed_content TEXT, ' +
                            'content_language TEXT ' +
                            ')')
        self.connection.commit()

    def close_spider(self, spider):
        if self.write_counter % self.write_chunks:
            # need to end the last transaction
            self.logger.debug('Writing chunk %s',self.write_counter)
            self.cursor.execute('END TRANSACTION')
            self.connection.commit()

        self.connection.close()

    # Take the item and put it in database - do not allow duplicates
    def process_item(self, item, spider):

        insert_sql = 'insert into jobsch (unique_id,url,posting_id,date_parsed,' + \
                        'date_published,source,job_title,location,occupation,job_rank,' \
                        'company_name,raw_content,parsed_content,content_language) ' + \
                        'values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'

        if not self.write_counter % self.write_chunks:
            # new transaction
            self.cursor.execute('BEGIN TRANSACTION')

        self.cursor.execute(insert_sql,(item['unique_id'], item['url'],
                                        item['posting_id'],
                                        item['date_parsed'],
                                        item['date_published'],
                                        item['source'],
                                        item['job_title'],
                                        item['location'],
                                        item['occupation'],
                                        item['job_rank'],
                                        item['company_name'],
                                        sqlite.Binary(item['raw_content']),
                                        item['parsed_content'],
                                        item['content_language']))

        self.write_counter = self.write_counter + 1
        self.connection.commit()

        if not self.write_counter % self.write_chunks:
            self.logger.debug('Writing chunk %s', self.write_counter)
            self.cursor.execute('END TRANSACTION')
            self.connection.commit()
        self.logger.info("Item stored")
        return item