import scrapy
import mylogging as logging
import sys
import os
import yaml


import urllib.parse as urlparse

from datetime import date

from scrapy import spiders

from .items import EkatteItem



class EkatteSpider(spiders.Spider):
    name = "spider_ekatte_pop"
    allowed_domains = ["nsi.bg"]

    def __init__(self, Name=name, **kwargs):
        super(EkatteSpider, self).__init__(Name, **kwargs)
        # get the params
        dir_path = os.path.dirname(os.path.realpath(__file__))
        params_f = os.path.join(dir_path, 'params.yml')
        try:
            params = yaml.load(open(params_f, 'r'))
        except (FileNotFoundError, yaml.YAMLError) as problem:
            # be explicit
            raise problem

        start_sid = params['start_sid']
        max_sid = params['max_sid']
        base_url = params['base_url']

        self.start_urls = [base_url + str(i) for i in range(start_sid, max_sid)]
       
    def parse(self, response):

        print("hello")
        # get the href to the next page
        href_next_page = self.get_next_page(response)
        if href_next_page is not None:
            request_next_page = scrapy.Request(href_next_page, callback=self.parse)
            yield request_next_page

        EkatteSpider.logger.info("Looking for all hrefs on page {}: xpath(//@href)".format(response.url))

        # extract all hrefs from the left sidebar of the current page
        job_hrefs = extract_all_job_hrefs(response, EkatteSpider.logger)
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
            EkatteSpider.logger.info("Extracted {} job hrefs from current page".format(str(len(job_hrefs))))
            EkatteSpider.logger.debug("Proceeds with parsing individual job hrefs")
            for job_href in job_hrefs:
                url = response.urljoin(job_href)
                request = scrapy.Request(url, callback=self.parse_job,
                                         meta={'search_term': current_search_term})
                yield request

    def parse_job(self, response):

        item = EkatteItem()

        # job-specific and company info
        item['job_title'] = extrtact_job_title(response, EkatteSpider.logger)
        item['company_name'], item['location'] = \
            extract_company_name_job_location(response, EkatteSpider.logger)
        item['job_rank'] = extract_job_rank(response, EkatteSpider.logger)
        item['occupation'] = extract_job_occupation(response, EkatteSpider.logger)
        item['job_categories'] = extract_categories(response, EkatteSpider.logger)
        item['search_term'] = response.meta.get('search_term')

        # web-page content
        item['raw_content'], item["parsed_content"] = \
            extract_raw_processed_content(response, EkatteSpider.logger)

        item['content_language'] = ""
        if item["parsed_content"] != "":
            item['content_language'] = langdetect.detect(item["parsed_content"])
            EkatteSpider.logger.debug("Detected '{}' as content "
                                    "language for posting {}".format(item['content_language'], response.url))

        # meta-info
        u = urlparse.urlparse(response.url)._replace(query='')  # remove the query part of the url

        item['url'] = urlparse.urlunparse(u)
        item['posting_id'] = extract_posting_id(item['url'], EkatteSpider.logger)

        item['unique_id'] = hash_posting(hash_fields=(item.get('posting_id', ''),
                                                      item.get('job_title', ''),
                                                      item.get('company_name', '')
                                                      ),
                                         logger=EkatteSpider.logger)
        item['source'] = get_base_url(item['url'])
        item['date_parsed'] = str(date.today())
        item['date_published'] = extract_job_date_published(response, EkatteSpider.logger)

        yield item