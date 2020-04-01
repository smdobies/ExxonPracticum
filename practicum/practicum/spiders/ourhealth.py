# -*- coding: utf-8 -*-

# These are the required packages need for this python file to run completely
import scrapy
from ..items import PracticumItem
from datetime import datetime

# We need to define a start url or the website we are interested in scraping
urls = 'https://ourhealthandenvironment.wordpress.com/'

# Defining the class statement to be executed. This contains the whole scraping process
class BlogSpiderSpider(scrapy.Spider):
    name = 'ourhealth'

    # Page_number will be the counter for our loop. This will allow the spider to loop
    # through multiple pages
    page_number = 2

    # This first function starts the request loading the provided url above
    def start_requests(self):
        yield scrapy.Request(url=urls,
                             callback=self.parse_front)

    # First parsing method. Scrapes the first Web page generated by the start_requests function.
    def parse_front(self, response):
        # article_links are the urls corresponding to each blog post. These need to be collected
        # to "go into" the blog post.
        article_links = response.xpath('//h1[@class="entry-title"]/a/@href')

        # extracts the links from the scraped article_links
        links_to_follow = article_links.extract()

        # This will loop through each link in the list of blog links. The response will "click"
        # on each blog to go into the blog post and the function will then call the parse_pages function
        for link in links_to_follow:
            yield response.follow(url=link,
                                  callback=self.parse_pages)

        # the next_page is to use the counter above to go to the next page. It adds 1 for each iteration
        # so that it will keep looping for the first 250 pages. This function will yield back to
        # parse_front to start to the scraping of the next page of blogs
        next_page = 'https://ourhealthandenvironment.wordpress.com/page/' + str(BlogSpiderSpider.page_number) + '/'
        if BlogSpiderSpider.page_number <= 250:
            BlogSpiderSpider.page_number += 1
            yield response.follow(next_page, callback=self.parse_front)

    # the parse_pages function collects the information from the individual blog posts.
    def parse_pages(self, response):

        # calls the items.py file. The items file specifies which data points are being collected
        items = PracticumItem()

        # These are the locators for this particular blog website. These locators can be found
        # in the HTML text of the website. these locators are specific for this website
        article_date = response.xpath('//time[(@class="entry-date")]').re(r"\w+\s\d{1,2},\s\d{4}")
        article_title = response.xpath('//h1[(@class = "entry-title")]//text()').extract()
        author = response.xpath('//span[(@class="author vcard")]//text()').re(r"[A-Z]\w+\s\w+")
        article_text = response.xpath('//div[(@class="entry-content")]//text()').extract()
        twitter = []

        # The article text is sometimes in seperate paragraphs so this "body" function
        # will combine the paragraphs into one
        body = ''
        for text in article_text:
            body = body + text

        # These 3 lines clean up the body by removing new lines, tabs, and carriage return
        body = body.replace('\r', '')
        body = body.replace('\n', '')
        body = body.replace('\t', '')

        # Error handling if certain extracts do not catch anything. his way we insert a blank string
        # so we can still insert the record into the database
        if len(twitter) > 0:
            items['twitter'] = twitter[0]
        else:
            items['twitter'] = ''
        if len(author) > 0:
            items['author'] = author[0]
        else:
            two_authors = response.xpath('//span[@class = "submitted-by"]//text()').extract()
            items['author'] = two_authors[0]
        if len(article_date) > 0:
            items['article_date'] = article_date[0]
        else:
            items['article_date'] = ''
        if len(article_date) > 0:
            items['article_title'] = article_title[0]
        else:
            items['article_title'] = ''
        items['article_url'] = response.request.url
        items['article_text'] = body
        items['timestamp'] = datetime.now()

        # The yield items will yield the extracted items and put through the pipeline.
        # The pipeline was specified in the settings file by uncommenting the code below:
        # ITEM_PIPELINES = {
        #     'practicum.pipelines.PracticumPipeline': 300,
        # }
        yield items
