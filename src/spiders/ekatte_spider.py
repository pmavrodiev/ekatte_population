import scrapy
import mylogging as logging
import sys
import os
import yaml
import re


import urllib.parse as urlparse

from datetime import date

from scrapy import spiders

from spiders.items import EkatteItem



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
        
        left_over = [6364, 6360, 6099]


        self.start_urls = [base_url + str(i) for i in range(start_sid, max_sid)]
        self.start_urls = self.start_urls + [base_url + str(i) for i in left_over]

       
       
    def parse(self, response):

        logging.info(f'Visiting {response.url}')
        
        table_summary = response.xpath("//table[@summary]")

        if len(table_summary) != 1:
            # there should be precisely one 'table' element with an 
            # attribute 'summary'
            logging.warning(f'{response.url}: {len(table_summary)} table '
                            f'elements. Skipping')
            return
        
        table = table_summary[0]

        caption_all = ''.join(table.xpath('//caption//text()').getall())
        #
        ekatte_list = re.findall(r'\d+', caption_all)
        if len(ekatte_list) != 1:
            # there should be only one EKATTE number
            logging.warning(f'{response.url}: {ekatte_list} is invalid. '
                            f'Skipping')
            return

        ekatte_str = ekatte_list[0]
        
        try:
            int(ekatte_str)
        except ValueError:
            logging.error(f'{response.url}: {ekatte_str} is invalid. Skipping')
            return

        # add left padding
        ekatte_str = ekatte_str.rjust(5, '0')
        
        table_rows = table.xpath('//tr/*[contains(@class, "cmid")]/..')

        logging.debug(f'{response.url}: {len(table_rows)} date entries')

        for row in table_rows:
            cols = row.xpath('.//td/text()')
            if len(cols) != 3:
                logging.error(f'{response.url}: Malformatted row. Skipping')
                continue

            date = cols[0].get()
            population_string = cols[1].get()
            try:
                population = int(population_string)
            except ValueError:
                logger.error(f'{response.url}: Population {population_string} '
                             f' is not a number. Skipping')
                continue

            item = EkatteItem()
            item['ekatte_str'] = ekatte_str
            item['date'] = date
            item['population'] = population

            yield item