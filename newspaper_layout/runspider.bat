set URLFILE = %1
set URLFILE_PATH="../snapshot-urls/%1.txt"
set OUTPUT_PATH="../reports"

set BASEFILE_NAME="%1_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set CSV_FILE="%OUTPUT_PATH%/%BASEFILE_NAME%.csv"

scrapy crawl newspaper_ia -a http_user=fbu -a http_pass=fhstpoelten -a url_file=%URLFILE_PATH% -o %CSV_FILE% --logfile %OUTPUT_PATH%/%BASEFILE_NAME%.log
python newspaper_layout/similarity-checker.py %CSV_FILE%