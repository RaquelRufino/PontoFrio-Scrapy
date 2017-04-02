# -*- coding: utf-8 -*-
import scrapy as spider
import logging
from scrapy.utils.response import open_in_browser
from scrapy.selector import Selector

from pontofrio.items import PontofrioItem
from scrapy.spiders.init import Spider

#Autor: Wellington Luiz
'''
    UNIVERSIDADE FEDERAL RURAL DE PERNAMBUCO - UFRPE
    Curso: Bacharelado em Sistemas de Informação
    Scrapy - Spider no site Pontofrio
    Retornar json com url,titulo, fotos, precoAvista, precoPrazo, prestacao.
    Executado em python 2.7

'''


class PontofrioSpider(Spider):
    name = "pontofrio_full"
    allowed_domains = ["pontofrio.com.br"]
    start_urls = [
        "https://carrinho.pontofrio.com.br/Checkout?ReturnUrl=http://www.pontofrio.com.br#login"
    ]

    # fazendo o Login
    def parse(self, response):
        return spider.FormRequest.from_response(
            response,
            formdata={'Email': 'seu login', 'Senha': 'sua senha'},
            callback=self.parse_after_login
        )

    #Depois de fazer o Login
    def parse_after_login(self, response):
        # Verifique o login bem-sucedido antes de continuar
        # logging.info(response.body)
        nomelogado = response.xpath('normalize-space(//*[@id="lblLoginMsg"]/text())').extract()[0]
        logging.info(str(nomelogado))
        if 'E-mail ou senha incorretos' in response.body:
            logging.error("---------------------------------------")
            logging.error("       NÃO FOI POSSÍVEL LOGAR          ")
            logging.error("---------------------------------------")
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
        items = response.xpath(
            ('//ul[@class="vitrineProdutos"]/li/div/a/@href')
        )
        proxima = response.xpath('//*[@id="ctl00_Conteudo_ctl04_divBuscaResultadoInferior"]/div/ul/li[@class="next"]//@href')

        for item in items:
            if item is not None:
                elem = PontofrioItem()
                # elem['url'] = response.url
                elem['titulo'] = response.xpath(
                    'normalize-space(//*[@id]/div/a/strong[2]//text())'
                ).extract()[0]
                elem['fotos'] = response.xpath(
                    '//*[@id]/div/a/span/img/@src').extract_first()

                preco = response.xpath(
                    'normalize-space(//*[@id]/div/a/span[2]/span[2]/strong/text())'
                ).extract()[0]
                if 'R$' in preco:
                    elem['precoAvista'] = preco
                else:
                    elem['precoAvista'] = "Indiponivel"

                precoRegular= response.xpath(
                    'normalize-space(//*[@id]/div/a/span[2]/span[1]/strong/text())'
                ).extract()[0]
                if  'R$' in precoRegular:
                    elem['precoPrazo']= precoRegular
                else:
                    elem['precoPrazo']= "Indiponivel"

                pretacao =  response.xpath(
                    'normalize-space(//*[@id]/div/a/span[2]/span[3]//text())'
                ).extract()[0]
                if  'R$'in pretacao:
                    elem['prestacao'] = pretacao
                else:
                    elem['prestacao'] ="Indiponivel"


                yield elem

        # Mudadno de página


        next_pages = sel.xpath(
            '//*[@id="ctl00_Conteudo_ctl05_divOrdenacao"]/div[2]/ul/li[@class="next"]/a/@href'
            # '//div[3]/div[1]/div[2]/ul/li/a/@href'
        )
        try:
            yield spider.Request(url = next_pages.extract()[0], callback = self.parse_detail)
        except:
            print('GAMER OVER!!')
        # try:
        #
        #     # for page in next_pages.extract()[0]:
        #     #         # next_page = response.urljoin(page)
        #     #         # logging.info('Next Page: {0}'.format(page))
        #     #         yield spider.Request(url=page, callback=self.parse_detail)
        # except:pass