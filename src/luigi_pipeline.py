import luigi

import mylogging as logging

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class TaskSpider(luigi.Task):
    # sqlite_db = generate_sqlite_fname()
    task_complete = False
    
    def run(self):
        #
        process = CrawlerProcess(get_project_settings())
        process.crawl("spider_ekatte_pop")
        process.start()
        self.task_complete = True

    def complete(self):
        # Make sure you return false when you want the task to run.
        # And true when complete
        return self.task_complete


if __name__ == "__main__":
    
    logging.info("Hello World")
    luigi.build([TaskSpider()], local_scheduler=True)