from scrapy.item import Item, Field


class EkatteItem(Item):
    # DONE
    unique_id = Field()  # a unique auto-generated ID for storing in DB
    # DONE
    posting_id = Field()  # the job posting id from the website
    # DONE
    url = Field()

    # parsing meta data
    # DONE
    date_parsed = Field()
    # DONE
    date_published = Field()
    # DONE
    source = Field()

    # job-specific info
    # DONE
    job_title = Field()
    # DONE
    location = Field()
    canton_short = Field()  # e.g. ZH
    canton_long = Field()  # e.g. Zurich
    contract_type = Field()  # e.g. Part Time, Full Time
    # DONE
    occupation = Field()  # e.g. 80-100%
    # DONE
    job_rank = Field()  # e.g. Employee, Manager, Position with responsibilities
    salary = Field()  # if available
    # DONE
    job_categories = Field()  # if available
    # DONE
    search_term = Field()  # which search term produced this job

    # company info
    # DONE
    company_name = Field()
    company_type = Field()
    industry = Field()
    n_employees = Field()
    company_website = Field()

    # web-page content
    # DONE
    raw_content = Field()  # the raw HTML (gzip-compressed)
    # DONE
    parsed_content = Field()  # just the text, no HTML formatting
    # DONE
    content_language = Field()  # the language of the job posting

    # 'active' flag, which gets updated regularly to check if a job has expired
    active = Field()