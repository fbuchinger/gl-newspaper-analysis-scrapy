import os

snapshot_url_dir = r"../snapshot-urls/2007-2017"
report_dir = r"../reports/2007-2017"


def build_filepath(dir, filename, extension='', build_abspath = True):
    if len(extension) > 0:
        filename = os.path.splitext(filename)[0] + extension
    if build_abspath is True:
        return os.path.abspath(os.path.join(dir, filename))
    return os.path.join(dir, filename)

def task_crawl_urls():
    """ Step 1: crawl and analyze the urls from the .txt files, dump out csv files"""
    for url_file in os.listdir(snapshot_url_dir):
        params = {
            "url_file_path": build_filepath(snapshot_url_dir, url_file),
            "csv_file": build_filepath(report_dir, url_file, '.csv', False),
            "log_file": build_filepath(report_dir, url_file, '.log')
        }

        yield {
            'name': url_file,
            'targets': [params['csv_file']],
            'actions': ['scrapy crawl newspaper_ia -a http_user=fbu -a http_pass=fhstpoelten -a url_file="%(url_file_path)s" -o "%(csv_file)s" --logfile "%(log_file)s"' % params]
        }

def task_calculate_similarity():
    """ Step 2: calculate similarity from the csv files """
    for url_file in os.listdir(snapshot_url_dir):
        params = {
            "csv_file": build_filepath(report_dir, url_file, '.csv'),
        }

        yield {
            'name': url_file,
            'file_dep': ['newspaper_layout/similarity-checker.py', params["csv_file"]],
            'actions': ['python newspaper_layout/similarity-checker.py %(csv_file)s' % params],
            'targets': ['%s_similarity.csv' % os.path.splitext(url_file)[0],
                        '%s_difference_screenshots.txt' % os.path.splitext(url_file)[0]]
        }

def task_capture_difference_screenshots():
    """ Step 3: capture screenshots for the urls of relevant difference """
    for url_file in os.listdir(snapshot_url_dir):
        params = {
            "screenshot_urlfile": build_filepath(report_dir, url_file, '_difference_screenshots.txt'),
            "logfile": build_filepath(report_dir, url_file, '_scrapy-screenshots.log'),
        }

        yield {
            'name': url_file,
            'file_dep': [params["screenshot_urlfile"]],
            'targets': ['%s.png' % params["screenshot_urlfile"]],
            'actions': ['scrapy crawl newspaper_screenshot -a http_user=fbu -a http_pass=fhstpoelten -a url_file="%(screenshot_urlfile)s" --logfile "%(logfile)s"' % params]
        }
