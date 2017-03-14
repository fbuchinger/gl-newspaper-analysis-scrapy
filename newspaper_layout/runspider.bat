set URLFILE = %1
set URLFILE_PATH=../snapshot-urls/%~1.txt
set OUTPUT_PATH=../reports

echo %URLFILE_PATH%
set OUTPUT_FOLDER=%OUTPUT_PATH%/%1_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%

md "%OUTPUT_FOLDER%"
set CSV_FILE= %OUTPUT_FOLDER%/%~1.csv



scrapy crawl newspaper_ia -a http_user=fbu -a http_pass=fhstpoelten -a url_file="%URLFILE_PATH%" -o "%CSV_FILE%" --logfile "%OUTPUT_FOLDER%/scrapy.log"
rem TODO: similarity checker invocation is wrong - CSV file not found!
python newspaper_layout/similarity-checker.py "%CSV_FILE%"
scrapy crawl newspaper_screenshot -a http_user=fbu -a http_pass=fhstpoelten -a url_file= "%OUTPUT_FOLDER%/difference_screenshots.txt" --logfile "%OUTPUT_FOLDER%/scrapy-screenshots.log"