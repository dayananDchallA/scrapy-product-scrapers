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
        self.start_urls = ['https://www.amazon.sg/s?k=vacuum+cleaner']
        
    # Parse through each Start URLs
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
            
    # Parse function: Scrape the webpage and store it
    def parse(self, response):
        prod_divs = response.xpath("//div[@data-component-type='s-search-result']")
        i = 1
        for prod_div in prod_divs:
            print(i)
            asin = prod_div.xpath('./@data-asin').extract()
            print(asin[0])
            asin = asin[0]
            url = prod_div.xpath('./div/span/div/div/div[2]/div[2]/div/div/div/div/div/h2/a/@href').extract()
            full_url = self.get_full_url(url[0])
            print(full_url)
            #self.item['url'] = full_url
            rating = prod_div.xpath('./div/span/div/div/div[2]/div[2]/div/div/div/div/div[2]/div/span/span/a/i/span/text()').extract()
            if rating:
                print(rating[0].split(' ')[0])
                user_rating = rating[0].split(' ')[0]
            else:
                user_rating = None
            users_reviewed = prod_div.xpath("./div/span/div/div/div[2]/div[2]/div/div/div/div/div[2]/div/span[2]/a/span/text()").extract()
            if users_reviewed:
                print(users_reviewed[0])
                users_rated = users_reviewed[0]
            else:
                users_rated = None
            #/div/span/div/div/div[2]/div[1]/div/div/span/a/div/img    
            image_url = prod_div.xpath("./div/span/div/div/div[2]/div[1]/div/div/span/a/div/img/@src").extract()
            if image_url:
                print(image_url[0])
                image = image_url[0]
            else:
                image = None
                
            i = i+1
            request = Request(full_url, callback=self.parse_product_page)
            request.meta['asin'] = asin
            request.meta['full_url'] = full_url
            request.meta['user_rating'] = user_rating
            request.meta['users_rated'] = users_rated
            request.meta['image_url'] = image
            yield request
        next_page_url = response.xpath("//li[@class='a-last']//a/@href").extract_first()
        if next_page_url:
            absolute_next_page_url = response.urljoin(next_page_url)
            yield scrapy.Request(absolute_next_page_url,dont_filter=False)
            
            
    def get_full_url(self,url_string):
        """Return complete url"""
        return "https://www.amazon.sg" + url_string
        
    def parse_product_page(self, response):
        price = response.xpath("//*[@id='unqualified-buybox-olp']/div/span/text()").extract()
        price1= response.xpath("//span[@id='price_inside_buybox']/text()").extract_first()
        price2 = response.xpath("//*[@id='buyNewSection']/div/div/span/span/text()").extract_first()
        self.item['asin'] = response.meta['asin']
        self.item['url'] = response.meta['full_url']
        self.item['rating'] = response.meta['user_rating']
        self.item['image'] = response.meta['image_url']
        self.item['users_rated'] = response.meta['users_rated']
        
        if price:
            print(price[0])
            print(self.get_symbol(price[0]))
            self.item['price'] = price[0]
            self.item['currency'] = self.get_symbol(price[0])
        elif price1:
            print(self.get_symbol(price1.strip()))
            self.item['price'] = price1.strip()
            self.item['currency'] = self.get_symbol(price1.strip())
        elif price2:
            print(self.get_symbol(price2.strip()))
            self.item['price'] = price2.strip()
            self.item['currency'] = self.get_symbol(price2.strip())
        else:
            self.item['price'] = None
            self.item['currency'] = None
            
        table_rows = response.xpath('//*[@id="productDetails_techSpec_section_1"]//tr')
        spec_data = []
        for table_row in table_rows:
            spec = table_row.xpath("./th/text()").extract_first().strip() 
            value = table_row.xpath("./td/text()").extract_first().strip()
            spec_data.append(spec+":"+value)
        print(spec_data)
        if spec_data:
            self.item['specs'] = ",".join(spec_data)
        else:
            self.item['specs'] = None
        yield self.item
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        
    def get_symbol(self,price):
        import re
        pattern =  r'(\D*)\d*\.?\d*(\D*)'
        g = re.match(pattern,price).groups()
        return g[0] or g[1]