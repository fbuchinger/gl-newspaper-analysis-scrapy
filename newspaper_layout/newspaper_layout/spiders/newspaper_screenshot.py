import json
import base64
from datetime import date, datetime, timedelta
import random
import os

import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest


lua_script = """
    function main(splash)
        splash:wait(0.5)
        splash:go(splash.args.url)
        splash:wait(1)


        local prepare_page_for_screenshot = splash:jsfunc([[
            function () {
                try {
                    var waybackInfo = document.getElementById('wm-ipp');
                    if(waybackInfo){
                        waybackInfo.parentNode.removeChild(waybackInfo);
                    }
               }
                catch (err){
                    return {snapshotURL: location.href, error: err.message }
                }
            }
        ]])

        prepare_page_for_screenshot()
        splash:set_viewport_full()
        return {
            png = splash:png()
        }
    end
"""

class NewspaperScreenshot(scrapy.Spider):
    name = 'newspaper_screenshot'
    http_user = 'myuser'
    http_pass = 'mypassword'

    # start_urls = ['http://www.orf.at']
    # start_urls = [l.strip() for l in open('urls.txt').readlines()]

    splash_args = {
        'lua_source': lua_script,
        'png': 1,
        'width': 1080,
        'render_all': 1,
        'wait': 10,
        'timeout': 180,
    }

    def __init__(self, snapshot_interval = '', test_url = None, url_file = None, *args, **kwargs):
        super(NewspaperScreenshot, self).__init__(*args, **kwargs)

        if url_file:
            self.url_file = url_file
            with open(url_file, 'r') as f:
                self.start_urls =[line.strip() for line in f.read().splitlines()]



    def parse (self, response):
        # TODO: add original request url and original request date here
        yield SplashRequest(response.url, self.parse_result, endpoint='render.png', args=NewspaperScreenshot.splash_args)
    
    def parse_result(self, response):
        # magic responses are turned ON by default,
        # so the result under 'html' key is available as response.body
        self.logger.info('Parse function called on %s', response.url)
        self.logger.info(dir(response))
        url = response.url
        filename = url[url.find("web.archive.org/web/") + 20:].replace(':', '_').replace('/', '_')
        save_name = os.path.splitext(self.url_file)[0]
        png_bytes = response.body
        png_file = open(save_name + filename +'.png','wb')
        png_file.write(png_bytes)
        png_file.close()
