# -*- coding: utf-8 -*-
import scrapy as spider
import logging
from scrapy.http import FormRequest
from pontofrio.items import PontofrioItem
from scrapy.utils.response import open_in_browser
from scrapy.selector import Selector


class PontofrioSpider(spider.Spider):
    name = "spider_pontofrio"
    allowed_domains = ["pontofrio.com.br"]
    start_urls = [
        "https://carrinho.pontofrio.com.br/Checkout?ReturnUrl=http://www.pontofrio.com.br#login"
    ]

    # fazendo o Login
    def parse(self, response):
        return [FormRequest.from_response(response,
                                          formdata={'Email': 'wellingtonluiz123456@gmail.com', 'Password': '123456'},
                                          callback=self.after_login)]

    def after_login(self, response):
        # Verifique o login bem-sucedido antes de continuar
        if "authentication failed" in response.body:
            logging.error("NãO FOI POSSIVEL LOGAR", level=logging.ERROR)
            return
        #Nós conseguimos autenticar, agora vamos pegar os dados que queremos! \o/
        else:
            logging.info("---------------------------------------")
            logging.info("       LOGIN EFETUADO COM SUCESSO      ")
            logging.info("---------------------------------------")
            open_in_browser(response)
            return spider.Request(url="http://www.pontofrio.com.br/Informatica/Computadores/?Filtro=C56_C58",
                                  callback=self.parse_detail)

    #Pegando os dados na pagina de computadores
    def parse_detail(self, response):
        sel = Selector(response)
        logging.info(response.url)
        items = sel.xpath(
            ('//ul[@class="vitrineProdutos"]/li/div/a/@href')
        )

        for item in items:
            if item is not None:
                elem = PontofrioItem()
                elem['url'] = response.url
                elem['titulo'] = response.xpath(
                    'normalize-space(//*[@id]/div/a/strong[2]//text())'
                ).extract()[0]
                elem['fotos'] = response.xpath(
                    '//*[@id]/div/a/span/img/@src').extract_first()
                elem['preco'] = response.xpath(
                    'normalize-space(//*[@id]/div/a/span[2]/span[2]/strong/text())'
                ).extract()[0]
                elem['precoRegular'] = response.xpath(
                    'normalize-space(//*[@id]/div/a/span[2]/span[1]/strong/text())'
                ).extract()[0]
                elem['prestacao'] = response.xpath(
                    'normalize-space(//*[@id]/div/a/span[2]/span[3]//text())'
                ).extract()[0]
                yield elem

        next_pages = response.xpath(
            '//*[@id="ctl00_Conteudo_ctl05_divOrdenacao"]/div[2]/ul/li[@class="next"]/a/@href'
        )
        #mudadno de página
        try:
            aux = None
            for page in next_pages.extract():
                if page != aux:
                    aux = page
                    # next_page = response.urljoin(page)
                    logging.info('Next Page: {0}'.format(page))
                    yield spider.Request(url=page, callback=self.parse_detail)
        except:pass