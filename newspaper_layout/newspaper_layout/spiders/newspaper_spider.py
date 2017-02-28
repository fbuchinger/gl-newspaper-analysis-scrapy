import json
import base64
from datetime import date, datetime, timedelta
import random

import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest

lua_script = """
    function main(splash)
         -- splash:autoload("https://rawgit.com/fbuchinger/jquery.layoutstats/master/src/layoutstats.js")
        -- splash:autoload("https://rawgit.com/fbuchinger/jquery.layoutstats/font-metrics-by-area/src/layoutstats.js")
        splash:autoload("https://rawgit.com/fbuchinger/jquery.layoutstats/css-classlist/src/layoutstats.js")
        splash:wait(0.5)
        splash:go(splash.args.url)
        splash:wait(1)

        ready_for_measurement = splash:jsfunc([[function() {
            var snapshotFrame = document.getElementById('replay_iframe');
            return window.layoutstats !== undefined && snapshotFrame && snapshotFrame.contentDocument && snapshotFrame.contentDocument.readyState === 'complete';
        }]])

        function wait_for(condition)
            local max_retries = 10
            while not condition() do
                splash:wait(0.5)
                max_retries = max_retries - 1
                if max_retries == 0 then break end
            end
        end

        local measure_layout = splash:jsfunc([[
            function measureLayout() {
                try {
                    var iframeDoc = document.getElementById('replay_iframe').contentDocument;
                    var waybackInfo = iframeDoc.getElementById('wm-ipp');
                    if(waybackInfo){
                        waybackInfo.parentNode.removeChild(waybackInfo);
                    }
                    var measurements = window.layoutstats(iframeDoc.body);
                    measurements.snapshotURL = location.href;
                    measurements.ISOTimeStamp = (new Date).toISOString();
                    if (measurements.textVisibleCharCount && measurements.textVisibleCharCount > 0) {
                        return measurements;
                    }
                    else {
                        window.setTimeout(measureLayout, 500);
                    }
                }
                catch (err){
                    return {snapshotURL: location.href, error: err.message }
                }
            }
        ]])

        wait_for(ready_for_measurement)
        return measure_layout()
    end
"""

def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

class NewspaperSpider(scrapy.Spider):
    name = 'newspaper_ia'
    http_user = 'myuser'
    http_pass = 'mypassword'

    custom_settings = {
        'IA_BASEURL': 'http://web.archive.org/web',
        'DAYS_BETWEEN_SNAPSHOTS': 30,
        'START_DATE': '2005-01-01',
        'END_DATE': '2015-01-01',
        #fields that should be exported in a CSV/JSON export
        # 'FEED_EXPORT_FIELDS': [
        #     'requested_url',
        #     'snapshot_date',
        #     'textTopFontColor',
        #     'textTopFont',
        #     'textTopFontSize',
        #     'textUniqueFontSizeCount',
        #     'textUniqueFontColorCount',
        #     'textUniqueFontCount',
        #     'textUniqueFonts',
        #     'textVisibleCharCount',
        #     'textTopFontStyle',
        #     'ISOTimeStamp',
        #     'version',
        #     'textFirst1000Chars',
        #     'newspaper'
        # ],
        'NEWSPAPERS':{
            'clarin': 'http://clarin.com',
            'presse': 'http://diepresse.com',
            'elpais': 'http://elpais.com',
            'guardian':'http://guardian.co.uk',
            'universal':'http://eluniversal.com.mx',
            'repubblica':'http://www.repubblica.it',
            'oglobo':'http://oglobo.globo.com',
            'sz':'http://www.sueddeutsche.de',
            'nytimes':'http://nytimes.com',
            'figaro':'http://lefigaro.fr',
        },
        'ANAYLISED_NEWSPAPERS': ['clarin','presse','elpais','guardian','universal','repubblica','oglobo','sz','nytimes','figaro']
    }
    # start_urls = ['http://www.orf.at']
    # start_urls = [l.strip() for l in open('urls.txt').readlines()]

    splash_args = {
        'html': 1,
         #'png': 1,
        'width': 600,
        'render_all': 1,
        'wait': 10,
        'timeout': 180,
        'lua_source': lua_script
    }

    def __init__(self, snapshot_interval = '', test_url = None, url_file = None, *args, **kwargs):
        super(NewspaperSpider, self).__init__(*args, **kwargs)
        self.snapshot_interval = safe_cast(snapshot_interval,int, self.custom_settings['DAYS_BETWEEN_SNAPSHOTS'])
        self.interval_days = timedelta(days = self.snapshot_interval)
        self.start_date = datetime.strptime(self.custom_settings['START_DATE'],'%Y-%m-%d')
        self.end_date = datetime.strptime(self.custom_settings['END_DATE'],'%Y-%m-%d')
        self.newspapers = self.custom_settings['NEWSPAPERS']

        #define the to-be analyzed newspapers
        if hasattr(self,'newspaper_list'):
               self.analysed_newspapers = self.newspaper_list.split(',')
        else:
            self.analysed_newspapers = self.custom_settings['ANAYLISED_NEWSPAPERS']

        if test_url is None:
            self.newspaper_urls = [self.newspapers[name] for name in self.analysed_newspapers]
            #if self.start_urls is None:
            self.start_urls = self.build_urls()
        else:
            self.start_urls = [test_url]

        if url_file:
            with open(url_file, 'r') as f:
                self.start_urls = f.read().splitlines()

    def build_urls (self):
        def perdelta(start, end, delta):
            curr = start
            while curr < end:
                yield curr
                curr += delta

        urls = []

        for snapshot_date in perdelta(self.start_date, self.end_date, self.interval_days):
            for newspaper_url in self.newspaper_urls:
                datestr = snapshot_date.strftime('%Y%m%d')
                url = '%s/%s/%s' % (self.custom_settings['IA_BASEURL'], datestr, newspaper_url)
                urls.append(url)

        random.shuffle(urls)
        return urls


    def parse (self, response):
        # TODO: add original request url and original request date here
        yield SplashRequest(response.url, self.parse_result, endpoint='execute', args=NewspaperSpider.splash_args)
    
    def parse_result(self, response):
        # magic responses are turned ON by default,
        # so the result under 'html' key is available as response.body
        #html = response.body

        # you can also query the html result as usual
        #title = response.css('title').extract_first()

        # full decoded JSON data is available as response.data:
        #png_bytes = base64.b64decode(response.data['png'])
        #filename = response.url.split('/')[4] + '.png'
        #with open(filename, 'wb') as f:
        #    f.write(png_bytes)
        #inspect_response(response, self)
        #print result
        self.logger.info('Parse function called on %s', response.url)
        result = json.loads(response.body)
        self.logger.info('JSON response: %s', response.body)
        result['requested_url'] = response.url

        yield result

if __name__ == "__main__":
    #scrapy crawl newspaper_ia -a test_url=http://web.archive.org/web/20090418200017/http://diepresse.com/ http://web.archive.org/web/20090514085159/http://www.elpais.com/ http://web.archive.org/web/20100106112048/http://www.sueddeutsche.de/ http://web.archive.org/web/20100507075606/http://www.repubblica.it/
    # n = NewspaperSpider(test_url="http://web.archive.org/web/20050105074106/http://www.sueddeutsche.de/")
    n = NewspaperSpider(snapshot_interval=30, newspaper_list="clarin")
    n.start_requests()
    # print len(n.build_urls())