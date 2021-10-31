import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from property import Property
from urllib.parse import urlparse


class LondonrelocationSpider(scrapy.Spider):
    name = 'londonrelocation'
    allowed_domains = ['londonrelocation.com']
    start_urls = ['https://londonrelocation.com/properties-to-rent/']

    def parse(self, response):
        for start_url in self.start_urls:
            yield Request(url=start_url,
                          callback=self.parse_area)

    def parse_area(self, response):
        area_urls = response.xpath('.//div[contains(@class,"area-box-pdh")]//h4/a/@href').extract()
        for area_url in area_urls:
            yield Request(url=area_url,
                          callback=self.parse_area_pages)

    def parse_area_pages(self, response):
        # Write your code here and remove `pass` in the following line
        for item in response.css('.test-inline'):
            property = ItemLoader(item=Property())
            property.add_value('title', item.css('.h4-space h4 a::text').get().strip())

            price_text = item.css('.bottom-ic h5::text').get().strip().split(" ")
            if "pw" in price_text:
                for i, x in enumerate(price_text):
                    if x.isnumeric():
                        price_text[i] = str(int(x) * 4)
                    elif x == "pw":
                        price_text[i] = "pcm"
            property.add_value('price', " ".join(price_text))

            parsed_uri = urlparse(response.request.url)
            base_url = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            property.add_value('url', base_url + item.css('.h4-space h4 a::attr("href")').get())

            yield property.load_item()
        for url in response.css('.pagination a::attr("href")').extract():
            if url and url.endswith("2"):
                yield response.follow(url, self.parse_area_pages)
        # an example for adding a property to the json list:
        # property = ItemLoader(item=Property())
        # property.add_value('title', '2 bedroom flat for rental')
        # property.add_value('price', '1680') # 420 per week
        # property.add_value('url', 'https://londonrelocation.com/properties-to-rent/properties/property-london/534465-2-bed-frognal-hampstead-nw3/')
        # return property.load_item()
