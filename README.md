Parsing job description from Indeed and Glassdoor with scrapy and selenium. Save data into S# bucket with python and typer CLI. Data processing in Ray clusters and save result in Redshift.
Run spiders with arguments:

.. sourcecode:: python

    scrapy crawl glassdoor-job-list -a query="united-states-data-analyst-jobs-SRCH_IL.0,13_IN1_KO14,26.htm?fromAge=7" -a item_target_count=150
    scrapy crawl indeed_job -a keyword="data scientist" -a location="United States"

.. Typer command:: create S3 bucket

    python -m bin.migrations aws create_bucket your bucket name

.. Typer command:: upload data into S3 bucket

    python -m bin.migrations web_to_gcs web_to_gcs my local path bucket name path

.. Typer command:: create connection Redshift database and execute query

    python -m bin.migrations redshift_conn query_database \
            --host host \
            --port port \
            --database database \
            --user user \
            --password *** \
            --query "select * from jobs" \
            --limit 10


    
