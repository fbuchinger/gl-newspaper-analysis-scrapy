import json
import base64
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
                $('#wm-ipp-inside').find('a[href="#close"]').trigger('click');
                var measurements = $('body').layoutstats('getUniqueFontStyles');
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
    #start_urls = ['http://www.orf.at']
    start_urls = [l.strip() for l in open('urls.txt').readlines()]
    splash_args = {
        'html': 1,
         #'png': 1,
        'width': 600,
        'render_all': 1,
        'wait': 10,
        'lua_source': lua_script
    }
    
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