import scrapy
from scrapy.item import Item
from scrapy_splash import SplashRequest
from scrapy.loader import ItemLoader
from teller.items import VehiclesPerson
import time
import logging

class QlSpider(scrapy.Spider):
    name = 'ql'
    http_user = 'user'
    http_pass = 'userpass'
    allowed_domains = []

    ad_script = '''
        function main(splash, args)
            splash.private_mode_enabled = false
            assert(splash:go(args.url))
            while not splash:select('div.jsx-2652633486.call-now') do
                splash:wait(40)
            end
            splash:set_viewport_full()
  			splash:wait(2)
            local call_button = assert(splash:select('div.jsx-2652633486.call-now'))
            splash:wait(0.2)
  			call_button:mouse_click()
            local email_button = assert(splash:select('div.jsx-2652633486.email-now'))
            splash:wait(0.2)
  			email_button:mouse_click()
            return splash:html()
        end
    
    '''
    main_page_script = '''
        function main(splash, args)
            assert(splash:go(args.url))
            assert(splash:wait(20))
            splash:set_viewport_full()
            splash:wait(3)
            assert(splash:select_all('div.//*[@class="col-sm-9 fixed-ratio disable-in-mobile"]/div/div/div/'))
            return splash:html()
        end 
       '''
    links_script = '''
        function main(splash, args)
            assert(splash:go(args.url))
            assert(splash:wait(20))
            splash:set_viewport_full()
            splash:wait(3)
            assert(splash:select_all('div.vehicle-row-image'))
            return splash:html()
        end
    '''
    next_page_script = '''
        function main(splash, args)
            assert(splash:go(args.url))
            assert(splash:wait(20))
            splash:set_viewport_full()
            splash:wait(10)
            local next_buttons = assert(splash:select_all('a.page-number'))
            assert(next_buttons[#next_buttons - 1]:mouse_click())
            assert(splash:wait(20))
            return  splash:html()
        end
    '''
    base = ""
    urls = []
    for i in range(1,466):
        urls.append(base+str(i))
    def start_requests(self):
        for url in self.urls:
            yield SplashRequest(url=url,
                                callback=self.parse_page, endpoint="execute", args={
                                'lua_source': self.links_script,
                                'wait': '2',
            })
    
    def parse_page(self, response):
        links = response.xpath('//div[@class="vehicle-row"]/a/@href').extract()
        logging.info(f"scrapping {len(links)} links")
        for link in links:
            logging.info(f"scraping link {link}")
            yield SplashRequest(response.urljoin(link), callback=self.parse_ad, endpoint="execute", 
                                args={
                                    'lua_source': self.ad_script,
                                    'timeout': 3600,
                                })



    def parse_ad(self, response):
        person = ItemLoader(item=VehiclesPerson(), response=response)
        
        person.add_xpath('phone', '//*[@id="left-side"]/div[5]/div/div[2]/div/p[2]/a/text()')
        person.add_xpath('email', '//*[@id="left-side"]/div[5]/div/div[4]/div/p[2]/text()')
        person.add_xpath('username', '//*[@id="left-side"]/div[5]/div/div[1]/a/text()')
        person.add_xpath('location', '//*[@id="left-side"]/div[5]/div/div[5]/p[2]/text()')
        return person.load_item()
