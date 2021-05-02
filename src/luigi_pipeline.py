import luigi
import ekatte_population.src.logging as logging

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class TaskSpider(luigi.Task):
    # sqlite_db = generate_sqlite_fname()
    task_complete = False
    
    search_terms = ['Team Leader', 'CEO', 'CTO', 'CFO',
                    'Consultant', 'Project Manager', 'Developer',
                    'Data Products Manager', 'Data Science',
                    'Full Stack Developer', 'Data Architect',
                    'Big Data Architect', 'Big Data Engineer',
                    'Data Scientist', 'Senior Data Scientist',
                    'Machine Learning Engineer', 'Quantitative Analyst',
                    'Data Engineer', 'Marketing', 'Digital Marketing',
                    'Physics', 'Power Electronics', 'Electrical Engineering',
                    'Risk Analyst', 'Risk', 'Architecture', 'Credit Risk', 'Biostatistician']

    def run(self):
        #
        process = CrawlerProcess(get_project_settings())
        process.crawl("spider_ekatte_pop", search_term=TaskSpider.search_terms)
        process.start()
        self.task_complete = True

    def complete(self):
        # Make sure you return false when you want the task to run.
        # And true when complete
        return self.task_complete


if __name__ == "__main__":
    # set up luigi logger
    logging.info("Hello World")
    luigi.build([TaskSpider()], local_scheduler=True)