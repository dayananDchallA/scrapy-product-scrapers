import scrapy
from selenium import webdriver
from time import sleep
from scrapy import Request
from testScrapy.items import TestscrapyItem

class ProductsSpider(scrapy.Spider):
    name = "products"
    item = TestscrapyItem()
    
    
    # Initalize the webdriver    
    def __init__(self):
        self.start_urls = ['https://www.flipkart.com/search?q=vaccum+cleaner']
        
    # Parse through each Start URLs
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
            
    # Parse function: Scrape the webpage and store it
    def parse(self, response):
        prod_divs = response.xpath("//div[@class='_1UoZlX']")
        for prod_div in prod_divs:
            url_string = prod_div.xpath("./a/@href").extract_first()
            full_url = self.get_full_url(url_string)
            yield Request(full_url, callback=self.parse_product_page)
            
        next_page_url = response.xpath("//span[text()='Next']/ancestor::a/@href").extract_first()
        print("NEXT PAGE: "+next_page_url)
        if next_page_url:
            print("NEXT PAGE: "+next_page_url)
            absolute_next_page_url = response.urljoin(next_page_url)
            print("NEXT URL: "+absolute_next_page_url)
            yield scrapy.Request(absolute_next_page_url,dont_filter=False)
            
    def parse_product_page(self, response):
        listed_price = response.xpath("//div[@class='_1uv9Cb']/div[1]/text()").extract_first()
        actual_price = response.xpath("//div[@class='_1uv9Cb']/div[2]/text()").extract()
        seller_name = response.xpath("//div[@id='sellerName']/span/span/text()").extract_first()
        rating = response.xpath("//div[@id='sellerName']/span/div/text()").extract_first()
        users_rated = response.xpath("//span[@class='_38sUEc']/span/span[1]/text()").extract_first()
        image_prop = response.xpath("//div[@class='_2_AcLJ']/@style").extract_first()
        start = image_prop.find("url(")
        end = image_prop.find(")")
        image = image_prop[(start-1)+len("url('"):end]
        currency = self.get_symbol(listed_price)
        asin_text = response.url.split("?")[1]
        asin_pid = asin_text.split("&")[0]
        asin = asin_pid.split("=")[1]
        
        specs = []
        spec_parts = response.xpath("//div[@class='_3WHvuP']/ul/li/text()").extract()
        for spec_part in spec_parts:
            specs.append(spec_part)
            
        print(listed_price)
        print("".join(actual_price))
        print(seller_name)
        print(rating)
        print(users_rated)
        print(currency)
        print(image)
        print(asin)
        print(specs)
        
        self.item['asin'] = asin
        self.item['url'] = response.url
        self.item['rating'] = rating
        self.item['image'] = image
        self.item['users_rated'] = users_rated
        self.item['listed_price'] = listed_price
        self.item['actual_price'] = "".join(actual_price)
        self.item['currency'] = currency
        self.item['specs'] = ",".join(specs)
        
        yield self.item
            
            
    def get_full_url(self,url_string):
        """Return complete url"""
        return "https://flipkart.com" + url_string
        
    def get_symbol(self,price):
        import re
        pattern =  r'(\D*)\d*\.?\d*(\D*)'
        g = re.match(pattern,price).groups()
        return g[0] or g[1]
            
