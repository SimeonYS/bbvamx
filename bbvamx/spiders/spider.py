import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BbvamxItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class BbvamxSpider(scrapy.Spider):
	name = 'bbvamx'
	start_urls = ['https://www.bbva.com/es/ultimas-noticias/']

	def parse(self, response):
		categories = response.xpath('//ul[@class="tagsLinks"]//a/@href').getall()
		yield from response.follow_all(categories, self.parse_category)

	def parse_category(self, response):
		post_links = response.xpath('//h2[@class="notTitulo"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//span[@class="date"]/text()').get()
		title = response.xpath('//h1[@class="article-title"]/text()').get()
		content = response.xpath('//div[@class="col-md-offset-2 col-md-8 col-sm-12 col-xs-12"]//text()[not (ancestor::div[@class="dataAuthor"]) and not (ancestor::div[@class="detContMedia rs_skip"]) and not (ancestor::figure) and not (ancestor::article[@class="col-md-12 col-sm-12 col-xs-12"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BbvamxItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
