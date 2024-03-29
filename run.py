from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from spiders.git_hub_crawler import GitHubCrawler

configure_logging()
settings = get_project_settings()
runner = CrawlerRunner(settings)

runner.crawl(GitHubCrawler)
# runner.crawl(ScottSportsComCrawler)

# Feel, Koga, Kalkhoff, Giant

d = runner.join()
d.addBoth(lambda _: reactor.stop())
reactor.run()
