scrapy crawl newspaper_ia -a http_user=fbu -a http_pass=fhstpoelten -a url_file="guardian-snapshoturls.txt" -o guardian_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.csv --logfile guardian_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log