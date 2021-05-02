import scrapy
import logging
import sys
import os
import langdetect
import urllib.parse as urlparse

from urllib.parse import parse_qs
from urllib.parse import quote

from datetime import date

from scrapy import spiders

from .items import JobItem
from src.simple_logging.custom_logging import setup_custom_logger
from src.src_scrapy.utils.parse_sidebar import extract_all_job_hrefs
from src.src_scrapy.utils.parse_job import extrtact_job_title
from src.src_scrapy.utils.parse_job import hash_posting
from src.src_scrapy.utils.parse_job import extract_posting_id
from src.src_scrapy.utils.parse_job import get_base_url
from src.src_scrapy.utils.parse_job import extract_raw_processed_content
from src.src_scrapy.utils.parse_job import extract_job_date_published
from src.src_scrapy.utils.parse_job import extract_company_name_job_location
from src.src_scrapy.utils.parse_job import extract_job_rank
from src.src_scrapy.utils.parse_job import extract_job_occupation
from src.src_scrapy.utils.parse_job import extract_categories

# as advised in the documentation, fix seed for deterministic behaviour on short texts
from langdetect import DetectorFactory
DetectorFactory.seed = 0


class JobsSpider(spiders.Spider):
    name = "spider_jobsch"
    allowed_domains = ["jobs.ch"]

    # set up the logger
    LOGGING_LEVEL = logging.INFO
    logger = setup_custom_logger('JobsSpider', LOGGING_LEVEL,
                                 flog=os.path.join(sys.path[0], "../logs/spider_jobsch.log"))

    def __init__(self, Name=name, **kwargs):
        super(JobsSpider, self).__init__(Name, **kwargs)

        base_url = "https://www.jobs.ch/en/vacancies/?term="
        # we need 'quote()' to add HTML spaces (%20) instead of normal spaces
        # self.start_urls = [base_url+quote(x) for x in kwargs['search_term']]
        self.start_urls = ["https://www.jobs.ch/en/vacancies/?term=Architecture"]

    def get_next_page(self, response):

        JobsSpider.logger.info("Looking for next page href on page {}".format(response.url))

        pattern_1 = '//a[@data-cy=\'paginator-next\']'
        pattern_2 = '//link[@rel=\'next\']'

        JobsSpider.logger.debug("Trying with pattern 1: {}".format(pattern_1))

        option_1 = response.xpath(pattern_1)
        # this will be a list, e.g.:
        # [<Selector xpath="//a[@data-cy='paginator-next']" data='<a data-cy="paginator-next" class="Li...'>]
        if len(option_1) == 0:
            # no next href - end of the data
            JobsSpider.logger.debug("Pattern 1 returned empty list - likely end of data")
            option_1 = None
        else:
            option_1 = option_1[0].attrib['href']
            JobsSpider.logger.debug("Pattern 1 returned: {}".format(option_1))

        JobsSpider.logger.debug("Trying with pattern 2: {}".format(pattern_2))
        option_2 = response.xpath(pattern_2)
        # this will be a list, e.g._
        # [<Selector xpath="//link[@rel='next']" data='<link data-rh="true" rel="next" href=...'>]
        if len(option_2) == 0:
            # no next href - end of the data
            JobsSpider.logger.debug("Pattern 2 returned empty list - likely end of data")
            option_2 = None
        else:
            option_2 = response.xpath(pattern_2)[0].attrib['href']
            JobsSpider.logger.debug("Pattern 2 returned: {}".format(option_2))

        if option_1 is None and option_2 is None:
            # quite likely end of data
            return None
        elif option_1 is None and option_2 is not None:
            # strange if this happens
            JobsSpider.logger.warning("Pattern 1 = None, Pattern 2 != None. Will return Pattern 2")
            next_page_href = response.urljoin(option_2)
        elif option_1 is not None and option_2 is None:
            # strange if this happens
            JobsSpider.logger.warning("Pattern 1 != None, Pattern 2 = None. Will return Pattern 1")
            next_page_href = response.urljoin(option_1)
        else:
            # neither are None, so they must contain valid hrefs
            next_page_href = response.urljoin(option_2)
            if option_1 != option_2:
                JobsSpider.logger.warning("Pattern 1 not the same as Pattern 2. Will return Pattern 2")

        return next_page_href

    def parse(self, response):

        # get the href to the next page
        href_next_page = self.get_next_page(response)
        if href_next_page is not None:
            request_next_page = scrapy.Request(href_next_page, callback=self.parse)
            yield request_next_page

        JobsSpider.logger.info("Looking for all hrefs on page {}: xpath(//@href)".format(response.url))

        # extract all hrefs from the left sidebar of the current page
        job_hrefs = extract_all_job_hrefs(response, JobsSpider.logger)
        parsed_url = urlparse.urlparse(response.url)
        current_search_term = "".join(parse_qs(parsed_url.query)['term'])

        """
        test_url = "https://www.jobs.ch/en/vacancies/detail/9546846/?jobposition=1-4&source=vacancy_search"
        url = response.urljoin(test_url)
        request = scrapy.Request(url, callback=self.parse_job)
        yield request
        return
        """

        if len(job_hrefs) > 0:
            JobsSpider.logger.info("Extracted {} job hrefs from current page".format(str(len(job_hrefs))))
            JobsSpider.logger.debug("Proceeds with parsing individual job hrefs")
            for job_href in job_hrefs:
                url = response.urljoin(job_href)
                request = scrapy.Request(url, callback=self.parse_job,
                                         meta={'search_term': current_search_term})
                yield request

    def parse_job(self, response):

        item = JobItem()

        # job-specific and company info
        item['job_title'] = extrtact_job_title(response, JobsSpider.logger)
        item['company_name'], item['location'] = \
            extract_company_name_job_location(response, JobsSpider.logger)
        item['job_rank'] = extract_job_rank(response, JobsSpider.logger)
        item['occupation'] = extract_job_occupation(response, JobsSpider.logger)
        item['job_categories'] = extract_categories(response, JobsSpider.logger)
        item['search_term'] = response.meta.get('search_term')

        # web-page content
        item['raw_content'], item["parsed_content"] = \
            extract_raw_processed_content(response, JobsSpider.logger)

        item['content_language'] = ""
        if item["parsed_content"] != "":
            item['content_language'] = langdetect.detect(item["parsed_content"])
            JobsSpider.logger.debug("Detected '{}' as content "
                                    "language for posting {}".format(item['content_language'], response.url))

        # meta-info
        u = urlparse.urlparse(response.url)._replace(query='')  # remove the query part of the url

        item['url'] = urlparse.urlunparse(u)
        item['posting_id'] = extract_posting_id(item['url'], JobsSpider.logger)

        item['unique_id'] = hash_posting(hash_fields=(item.get('posting_id', ''),
                                                      item.get('job_title', ''),
                                                      item.get('company_name', '')
                                                      ),
                                         logger=JobsSpider.logger)
        item['source'] = get_base_url(item['url'])
        item['date_parsed'] = str(date.today())
        item['date_published'] = extract_job_date_published(response, JobsSpider.logger)

        yield item