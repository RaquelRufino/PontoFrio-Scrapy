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

