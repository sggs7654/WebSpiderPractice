# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest


class ExampleSpider(scrapy.Spider):
    name = 'connect_splash'
    
    def start_requests(self):
        url = 'http://www.baidu.com'
        script = """
        assert(splash:go(args.url))
        assert(splash:wait(args.wait))
        return {html = splash:html()}
        """
        yield SplashRequest(url, self.parse, endpoint='run', args={'lua_source':script,'wait':3})
        
    def parse(self, response):
        from scrapy.shell import inspect_response
        inspect_response(response, self)
        pass
