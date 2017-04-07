#### Utilizando Scrapy para extrair dados do Pontofrio
#### Site: http://www.pontofrio.com.br/

#### Tutorial


```
$ rethinkdb
$ git clone https://github.com/wellington16/PontoFrio-Scrapy
$ pip install -r requirements.txt
$ cd PontoFrio-Scrapy
$ scrapy crawl pontofrio_full -o resultado.json -t json
``` 

#### Índice
  * [Objetivos](https://github.com/wellington16/PontoFrio-Scrapy/blob/master/README.md#objetivos)
  * Arquivos:
      * [pontoFrio.py](https://github.com/wellington16/PontoFrio-Scrapy/blob/master/pontofrio/spiders/spider-pontoFrio.py)
      * [pipelines.py](https://github.com/wellington16/PontoFrio-Scrapy/blob/master/pontofrio/pipelines.py)
      * [settings.py](https://github.com/wellington16/PontoFrio-Scrapy/blob/master/pontofrio/settings.py)
      * [items.py](https://github.com/wellington16/PontoFrio-Scrapy/blob/master/pontofrio/items.py)
      * [Login.py (EM OUTRO SITE)](https://github.com/wellington16/PontoFrio-Scrapy/blob/master/pontofrio/Login.py)
  * [Tempo gasto](https://github.com/wellington16/PontoFrio-Scrapy/blob/master/README.md#tempo-gasto)
  * [Programas utilizados](https://github.com/wellington16/PontoFrio-Scrapy/blob/master/README.md#programas-utilizados)
  * [Referências](https://github.com/wellington16/PontoFrio-Scrapy/blob/master/README.md#referências)


#### Objetivos
- [x] Utilização de ```xpath``` nas buscas por links
- [x] Persistência das informações (Para persistir foi usado RethinkDB como padrão, mas tamném foi testado no MongoDB e PostgreSQL)
- [x] Submissão de formulários
- [x] Manipulação de querystrings
- [x] Tratamento de paginação
- [x] Utilização de logs para sinalizar ocorrências durante o scraping


#### Arquivo: [pontoFrio.py](https://github.com/wellington16/PontoFrio-Scrapy/blob/master/pontofrio/spiders/spider-pontoFrio.py)
```python 
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
```

#### Arquivo: [pipelines.py](https://github.com/wellington16/PontoFrio-Scrapy/blob/master/pontofrio/pipelines.py)
```python
# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

###########################
######	EM MOGODB #########
###########################
# import pymongo
#
# class PontofrioPipeline(object):
#     collection_name = 'computadores'
#
#     def __init__(self, mongo_uri, mongo_db):
#         self.mongo_uri = mongo_uri
#         self.mongo_db = mongo_db
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls(
#             mongo_uri=crawler.settings.get('MONGODB_URL'),
#             mongo_db=crawler.settings.get('MONGODB_DB', 'defautlt-test')
#         )
#
#     def open_spider(self, spider):
#         self.client = pymongo.MongoClient(self.mongo_uri)
#         self.db = self.client[self.mongo_db]
#
#     def close_spider(self, spider):
#         self.client.close()
#
#     def process_item(self, item, spider):
#         self.db[self.collection_name].insert(dict(item))
#         return item
###########################

'''
	EM RETHINKDB
'''

import rethinkdb as r


class PontofrioPipeline(object):

    conn = None
    rethinkdb_settings = {}

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings

        rethinkdb_settings = settings.get('RETHINKDB', {})

        return cls(rethinkdb_settings)

    def __init__(self, rethinkdb_settings):
        self.rethinkdb_settings = rethinkdb_settings

    def open_spider(self, spider):
        if self.rethinkdb_settings:
            self.table_name = self.rethinkdb_settings.pop('table_name')
            self.db_name = self.rethinkdb_settings['db']
            self.conn = r.connect(**self.rethinkdb_settings)
            table_list = r.db(self.db_name).table_list().run(
                self.conn
            )
            if self.table_name not in table_list:
                r.db(self.db_name).table_create(self.table_name).run(self.conn)

    def close_spider(self, spider):
        if self.conn:
            self.conn.close()

    def process_item(self, item, spider):
        if self.conn:
            r.table(self.table_name).insert(item).run(self.conn)
        return item
```

#### Arquivo: [settings.py](https://github.com/wellington16/PontoFrio-Scrapy/blob/master/pontofrio/settings.py)
```python
# -*- coding: utf-8 -*-

# Scrapy settings for pontofrio project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#

'''
PARA O RETHINKDB
''' 


BOT_NAME = 'pontofrio'

SPIDER_MODULES = ['pontofrio.spiders']
NEWSPIDER_MODULE = 'pontofrio.spiders'

RETHINKDB = { 'table_name': 'items', 'db': 'banco_ponto_frio' }
ITEM_PIPELINES = { 'pontofrio.pipelines.PontofrioPipeline'}
DOWNLOAD_HANDLERS = {
  's3': None,
}

###########################
######	PARA O MOGODB #####
###########################
# MONGODB_URL = "localhost:27017"
# MONGODB_DB = "banco_ponto_frio"
#
# # Configure item pipelines
# ITEM_PIPELINES = {
#     'pontofrio.pipelines.PontofrioPipeline',
# }



# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'pontofrio (+http://www.yourdomain.com)'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS=32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY=3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
#COOKIES_ENABLED=False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED=False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'pontofrio.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'pontofrio.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'pontofrio.pipelines.SomePipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
#AUTOTHROTTLE_ENABLED=True
# The initial download delay
#AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'
```

#### Arquivo: [items.py](https://github.com/wellington16/PontoFrio-Scrapy/blob/master/pontofrio/items.py)
```python
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class PontofrioItem(scrapy.Item):
    fotos = scrapy.Field()
    url = scrapy.Field()
    codigo = scrapy.Field()
    titulo = scrapy.Field()
    precoAvista = scrapy.Field()
    precoPrazo = scrapy.Field()
    prestacao = scrapy.Field()

```
 #### Arquivo: [Login.py](https://github.com/wellington16/PontoFrio-Scrapy/blob/master/pontofrio/Login.py)
```python

# -*- coding: utf-8 -*-

import scrapy

from scrapy.spiders import Spider
from scrapy.utils.response import open_in_browser

#Autor: Wellington Luiz
'''
    UNIVERSIDADE FEDERAL RURAL DE PERNAMBUCO - UFRPE
    Curso: Bacharelado em Sistemas de Informação
    Scrapy - Login
    Retornar response com as informações da conta logada.
    Executado em python 2.7
'''

class LoginSpider(Spider):
    name = "linkedin"
    start_urls = [
        'https://www.linkedin.com/'
    ]

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'session_key': 'email@gmail.com',
                      'session_password': 'senha'},
            callback=self.depois_do_login
        )

    def depois_do_login(self, response):
        # check login succeed before going on
        if 'login-error' in response.body:
            self.logger.error("Falhou ao logar. ")
        else:
            self.logger.info("Logado com sucesso")
        yield scrapy.Request(url='https://www.linkedin.com/feed/?trk=hb_signin', callback=self.parse_detail)

    def parse_detail(self, response):
        open_in_browser(response)

```
 
#### Tempo gasto
  * Estudando: 15
  * Implementando: 5
  * Ajustando: 4
	

#### Programas utilizados
  * [XPath Helper](https://chrome.google.com/webstore/detail/xpath-helper/hgimnogjllphhhkhlmebbmlgjoejdpjl)
  * [Scraper](https://chrome.google.com/webstore/detail/scraper/mbigbapnjcgaffohmbkdlecaccepngjd)
  * [RethinkDB](https://www.rethinkdb.com/docs/install/)
  * [MongoDB](https://docs.mongodb.com/master/tutorial/install-mongodb-on-amazon/?_ga=1.85742745.1270707873.1490984659)
  * [PostgreSQL](https://www.postgresql.org/download/linux/)
  

#### Referências
  * [Scrapy 0.24 documentation [ENG]](https://doc.scrapy.org/en/0.24/)
  * [Guia de 10min com RethinkDB e Python [ENG]](https://www.rethinkdb.com/docs/guide/python/)
  * [MongoDB Documentation [ENG]](https://docs.mongodb.com/)
  * [Parte I - Configurando e rodando o Scrapy](http://www.gilenofilho.com.br/usando-o-scrapy-e-o-rethinkdb-para-capturar-e-armazenar-dados-imobiliarios-parte-i/)
  * [Parte II - Instalando, configurando e armazenando os dados no Rethinkdb](http://www.gilenofilho.com.br/usando-o-scrapy-e-o-rethinkdb-para-capturar-e-armazenar-dados-imobiliarios-parte-ii/)
  * [Parte III - Deploy do projeto Scrapy](http://www.gilenofilho.com.br/usando-o-scrapy-e-o-rethinkdb-para-capturar-e-armazenar-dados-imobiliarios-parte-iii/)
  * [XPath Tutorial [ENG]](https://www.w3schools.com/xml/xpath_intro.asp)
  * [Web Scraping with Python[ENG]](http://pdf.th7.cn/down/files/1603/Web%20Scraping%20with%20Python.pdf)
  * [Documentation PostgreSQL[ENG]](https://www.postgresql.org/docs/)
