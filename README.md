Run spiders with arguments:

.. sourcecode:: python

    scrapy crawl glassdoor-job-list -a query="united-states-data-analyst-jobs-SRCH_IL.0,13_IN1_KO14,26.htm?fromAge=7" -a item_target_count=150
    scrapy crawl indeed_job -a keyword="data scientist" -a location="United States"
