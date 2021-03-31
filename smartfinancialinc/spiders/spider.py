import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import SmartfinancialincItem
from itemloaders.processors import TakeFirst


class SmartfinancialincSpider(scrapy.Spider):
	name = 'smartfinancialinc'
	start_urls = ['https://www.smartfinancialinc.com/feed/PressRelease.svc/GetPressReleaseList?apiKey=BF185719B0464B3CB809D23926182246&LanguageId=1&bodyType=3&pressReleaseDateFilter=3&categoryId=1cb807d2-208f-4bc3-9133-6a9ad45ac3b0&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year=-1&excludeSelection=1']

	def parse(self, response):
		data = json.loads(response.text)
		for post in data['GetPressReleaseListResult']:
			url = post['LinkToDetailPage']
			date = post['PressReleaseDate']
			title = post['Headline']
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date, 'title': title})

	def parse_post(self, response, title, date):
		if 'pdf' in response.url:
			return
		description = response.xpath('//div[@class="module_body"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=SmartfinancialincItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
