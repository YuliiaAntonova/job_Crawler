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

.. Typer command:: upload data from s3 bucket to redshift

    python -m bin.migrations aws_to_redshift aws_to_redshift
           --host your_host
           --port your_port
           --database your_database
           --user your_user 
           --password your_password
           --access_key your_access_key 
           --secret_key your_secret_key --s3_
             location your_s3_location

.. Salary Prediction using job descriptions

The data comes from indeed and glassdoor sites and build a modl for predicting salary values depending job description metrics. This model deployed with Fastapi.



    
