import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerProcess
import emailTrack
from emailTrack import EmailtrackSpider


def scrapeEmail(urls):
    process = CrawlerProcess()
    for website in urls:
        process.crawl(EmailtrackSpider, url=f"https://{website}", cleanURL=website)
    process.start()


'''
webs = ['thedmregroup.com', 'evasachmanturek.com', 'stachurskarealestate.com']
print(range(len(webs)), ' : range')
scrapeEmail(webs)
'''