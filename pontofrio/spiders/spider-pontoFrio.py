# -*- coding: UTF-8 -*-
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
            yield spider.Request(url="http://www.pontofrio.com.br/Informatica/Computadores/?Filtro=C56_C58",
                               callback=self.parse_Scrapy)

    #Pegando os dados na pagina de computadores
    def parse_Scrapy(self, response):
        sel = Selector(response)
        items = response.xpath(
            ('//ul[@class="vitrineProdutos"]/li/div/a/@href')
        ).extract()

        for item in items:
            next_item = response.urljoin(item)
            logging.info(next_item)

            yield spider.Request(next_item, callback=self.parse_items)


        # Mudadno de página
        next_pages = sel.xpath(
            '//*[@id="ctl00_Conteudo_ctl05_divOrdenacao"]/div[2]/ul/li[@class="next"]/a/@href'
        )
        try:
            # pass
            yield spider.Request(url = next_pages.extract()[0], callback = self.parse_Scrapy, errback= self.parse_error(response))
        except:
            logging.info('GAMER OVER!!')

    def parse_items(self,response):

        elem = PontofrioItem()
        elem['url'] = response.xpath('//*[@id]/div/a/@href').extract_first()
        elem['titulo'] = response.xpath(
            'normalize-space(//*[@id="ctl00_Conteudo_ctl36_Content"]/div)'
        ).extract()[0]
        #
        elem['codigo'] = response.xpath('///*[@id="ctl00_Conteudo_upMasterProdutoBasico"]/div[2]/div/span[1]/text()').extract_first()
        elem['fotos'] = response.xpath(
            '//*[@id="ctl00_Conteudo_ctl07_prodImagens_imgFullImage"]//@src').extract()[0]

        preco = response.xpath(
            'normalize-space(//*[@id="ctl00_Conteudo_ctl01_precoPorValue"])'
        ).extract()[0]
        if 'R$' in preco:
            elem['precoAvista'] = preco
        else:
            elem['precoAvista'] = "Indiponivel"

        precoRegular = response.xpath(
            'normalize-space(//*[@id="ctl00_Conteudo_ctl01_precoDeValue"])'
        ).extract()[0]
        if 'R$' in precoRegular:
            elem['precoPrazo'] = precoRegular
        else:
            elem['precoPrazo'] = "Indiponivel"

        pretacao = response.xpath(
            'normalize-space(//*[@id="ctl00_Conteudo_ctl05_divParcCartaoOutrosCartoes"])'
        ).extract()[0]
        if 'R$' in pretacao:
            elem['prestacao'] = pretacao
        else:
            elem['prestacao'] = "Indiponivel"
        yield elem

    def parse_error(self, failure):
        logging.error('Nao foi possivel: {}'.format(failure.url))