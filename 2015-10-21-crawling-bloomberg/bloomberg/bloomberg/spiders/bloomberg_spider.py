import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

from time import mktime, strptime, localtime


class BloombergSpider(CrawlSpider):
    topic_constraint = ''
    
    name = 'bloomberg'
    start_urls = ['http://www.bloomberg.com/topics/tech']
    allowed_domains = ['bloomberg.com']
    
    rules = (
        Rule(
            LinkExtractor(allow=('topics/.*')),
        ),
        Rule(
            LinkExtractor(allow=('news/articles/2015-\d{2}-\d{2}/.*')),
            callback='parse_article'
        ),
    )
    custom_settings = {'mongo_collection_name': 'articles'}

    def parse_article(self, response):
        # read next
        for url in response.css(
                'div.read-this-next-view li>a::attr("href")'
        ).extract():
            yield scrapy.Request(response.urljoin(url), self.parse_article)

        # follow tags
        tags = response.css(
            'div.article-tags li>a::attr("href")'
        ).extract()
        for url in tags:
            yield scrapy.Request(response.urljoin(url))

        # constraining the topic
        if (not BloombergSpider.topic_constraint or
            BloombergSpider.topic_constraint in tags):
            
            # add the item
            title = response.css(
                'article h1[itemprop*=headline] span::text'
            ).extract()[0]

            body = response.css(
                'article div.article-body__content p::text'
            ).extract()
            
            publish_time = response.css(
                'div.published-info time.published-at::attr(datetime)'
            ).extract()[0]

            try:
                publish_time = mktime(strptime(publish_time,
                                               '%Y-%m-%dT%H:%M:%S.%fZ'))
            except TypeError:
                print("Invalid time {}".format(publish_time))
            
            yield {
                'url': response.url,
                'title': title,
                'body': body,  # TODO: compress it!
                'tags': tags,
                'publish_time': publish_time,
                'crawled_time': mktime(localtime())
            }
