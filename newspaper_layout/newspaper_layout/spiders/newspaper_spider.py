import json
import base64
from datetime import date, datetime, timedelta

import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest

lua_script = """
    function main(splash)
        splash:autoload("https://code.jquery.com/jquery-2.1.3.min.js")
        splash:autoload("https://raw.githubusercontent.com/fbuchinger/jquery.layoutstats/master/src/jquery.layoutstats.js")
        splash:wait(0.5)
        splash:go(splash.args.url)
        local measure_layout = splash:jsfunc([[
            function measureLayout() {
                jQuery('#wm-ipp-inside').find('a[href="#close"]').trigger('click');
                var measurements = jQuery('body').layoutstats('getUniqueFontStyles');
                measurements._id = location.href;
                measurements.ISOTimeStamp = (new Date).toISOString();
                if (measurements.textVisibleCharCount && measurements.textVisibleCharCount > 0) {
                    return measurements;
                }
                else {
                    window.setTimeout(measureLayout, 500);
                }
            }
        ]])
        return measure_layout()
    end
"""

class NewspaperSpider(scrapy.Spider):
    name = 'newspaper_ia'
    #start_urls = ['https://web.archive.org/web/20140314230711/http://www.theguardian.com/us']
    # start_urls = ['http://www.orf.at']
    # start_urls = [l.strip() for l in open('urls.txt').readlines()]
    custom_settings = {
        'IA_BASEURL': 'http://web.archive.org/web',
        'DAYS_BETWEEN_SNAPSHOTS': 365,
        'START_DATE': '2005-01-01',
        'END_DATE': '2015-01-01',
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

    splash_args = {
        'html': 1,
         #'png': 1,
        'width': 600,
        'render_all': 1,
        'wait': 10,
        'lua_source': lua_script
    }

    def __init__(self, *args, **kwargs):
        super(NewspaperSpider, self).__init__(*args, **kwargs)
        self.interval_days = timedelta(days = self.custom_settings['DAYS_BETWEEN_SNAPSHOTS'])
        self.start_date = datetime.strptime(self.custom_settings['START_DATE'],'%Y-%m-%d')
        self.end_date = datetime.strptime(self.custom_settings['END_DATE'],'%Y-%m-%d')
        self.analysed_newspapers = self.custom_settings['ANAYLISED_NEWSPAPERS']
        self.newspapers = self.custom_settings['NEWSPAPERS']

        self.newspaper_urls = [self.newspapers[name] for name in self.analysed_newspapers]
        #if self.start_urls is None:
        self.start_urls = self.build_urls()

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
        return urls


    def parse (self, response):
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
        result = json.loads(response.body)
        yield result

if __name__ == "__main__":
    n = NewspaperSpider()
    print len(n.build_urls())