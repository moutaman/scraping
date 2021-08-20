import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_splash import SplashRequest
import logging
from teller.items import VehiclesPerson
from scrapy.loader import ItemLoader
import pymongo

class QlfurSpider(scrapy.Spider):
    name = 'qlfur'
    allowed_domains = []
    http_user = ''
    http_pass = ''

    ad_script = '''
        function main(splash, args)
            splash.private_mode_enabled = false
            assert(splash:go(args.url))
            while not splash:select('div.call-now') do
                splash:wait(40)
            end
            splash:set_viewport_full()
  			splash:wait(4)
            local agree = splash:select('#qc-cmp2-ui > div.qc-cmp2-footer.qc-cmp2-footer-overlay.qc-cmp2-footer-scrolled > div > button.sc-ifAKCX.ljEJIv')
            agree:mouse_click()
            splash:wait(2)
            local call_button = assert(splash:select('div.call-now'))
            splash:wait(0.2)
  			call_button:mouse_click()
            local email_button = assert(splash:select('div.email-now'))
            splash:wait(0.2)
  			email_button:mouse_click()
            return splash:html()
        end
    '''
    links_script = '''
        function main(splash, args)
            assert(splash:go(args.url))
            assert(splash:wait(20))
            splash:set_viewport_full()
            splash:wait(3)
            assert(splash:select_all('div.listing-wapper'))
            return splash:html()
        end
    '''

    base = ""
    urls = []
    for i in range(1,327):
        urls.append(base+str(i))

    def start_requests(self):
        for url in self.urls:
            yield SplashRequest(url=url,
                                callback=self.parse_page, endpoint="execute", args={
                                'lua_source': self.links_script,
                                'wait': '2',
                                'timeout': 3600,
            })

    def parse_page(self, response):
        links = response.xpath('//div[@class="vehicle-row"]/@href').extract()
        logging.info(f"scrapping {len(links)} links")
        for link in links:
            logging.info(f"scraping link {link}")
            yield SplashRequest(response.urljoin(link), callback=self.parse_item, endpoint="execute", 
                                args={
                                    'lua_source': self.ad_script,
                                    'timeout': 3600,
                                })

    def parse_item(self, response):
        person = ItemLoader(item=VehiclesPerson(), response=response)
        
        person.add_xpath('phone', '//*[@id="left-side"]/div[3]/div/div[2]/div/p[2]/a/text()')
        person.add_xpath('email', '//*[@id="left-side"]/div[3]/div/div[4]/div/p[2]/a/text()')
        person.add_xpath('username', '//*[@id="left-side"]/div[3]/div/div[1]/a/text()')
        person.add_xpath('location', '//*[@id="__next"]/div/div/div[2]/div/div/div[3]/div/p[2]/text()')
        return person.load_item()