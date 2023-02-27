from array import array
from asyncio import exceptions
import enum
from time import strftime
from wsgiref import headers
import requests
from config import Config
import json
from types import SimpleNamespace
import urllib.parse
from datetime import datetime, timedelta


class typeFilter(enum.Enum):
    ALL_REGISTERS            = 0
    CHANGE_TODAY_ADDRESS     = 1
    CHANGE_TODAY_PHONE       = 2
    CHANGE_TODAY_OBSERVATION = 3
    CHANGE_TODAY_PERSON      = 4
    CHANGE_TODAY_CONTACT     = 5
    CHANGE_TODAY_STATISTIC   = 6
    CHANGE_TODAY             = 7

class ERP():
    
    def __init__(self,_cfg:Config) -> None:
        self.config = _cfg
        pass


    def __get_header(self) -> str:
        authorization = self.token.token_type+" "+self.token.access_token
        return {
            "Authorization": authorization,
            "Content-Type":"application/json",
            "Accept":"*/*",
            "Accept-Encoding":"gzip,deflate,br",
            "Connection":"keep-alive"
        }


    def get_token(self) -> str | None:
        """Metodo que realiza a conexao com a API do ERP e busca o token

        Returns:
            str | None: Objeto JSON ou Nada
        """
        #realiza a conexao e busca o access_token
        resp = requests.post("https://api.labellamafia.com.br:9443/api/totvsmoda/authorization/v2/token",data={
            "grant_type": self.config.get().erp.grant_type,
            "client_id": self.config.get().erp.client_id,
            "client_secret": self.config.get().erp.client_secret,
            "username": self.config.get().erp.username,
            "password": self.config.get().erp.password
        })
        if resp.status_code==200:
            self.token = json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
        else:
                print("Erro: "+urllib.parse.unquote(resp.text))
        return None


    def customer_list(self,_page:int = 1, _filter:typeFilter = typeFilter.ALL_REGISTERS) -> str | None:
        """Metodo que lista todos os clientes do ERP
        
        Args:
            _page (int, optional): pagina de registros. Defaults to 1.
            _filter (typeFilter, optional): tipo de filtro que serah aplicado (consultar arquivo config.py). Defaults to typeFilter.ALL_REGISTERS.
            
        Returns:
            str | None: Objeto JSON ou Nada
        """

        if _filter==typeFilter.ALL_REGISTERS:
            #print("Todos os registros")
            change = ""
        else:
            change = """ "change":{ 
                    \"startDate\": \""""+strftime("%Y-%m-%dT00:00:00.000Z")+"""\",
                    \"endDate\": \""""+strftime("%Y-%m-%dT23:59:59.999Z")+"""\"
                    },"""
            if _filter==typeFilter.CHANGE_TODAY_ADDRESS:
                #print("endereco")
                change = change + """
                    \"inAddress\": true
                },"""
            if _filter==typeFilter.CHANGE_TODAY_PHONE:
                #print("telefone")
                change = change + """
                    \"inPhone\": true
                },"""
            if _filter==typeFilter.CHANGE_TODAY_OBSERVATION:
                #print("observacao")
                change = change + """
                    \"inObservation\": true
                },"""
            if _filter==typeFilter.CHANGE_TODAY_CONTACT:
                #print("contato")
                change = change + """
                    \"inContact\": true
                },"""
            if _filter==typeFilter.CHANGE_TODAY_STATISTIC:
                #print("estatisticas")
                change = change + """
                    \"inStatistic\": true
                },"""

        body = """{
            \"filter\":{
                """+change+"""
                \"isCustomer\": true,
                \"isRepresentative\": false
            },
            \"option\":{
                \"branchStaticDataList\": [1]
            },
            \"expand\": \"phones,addresses,emails\",
            \"page\":"""+str(_page)+"""
        }"""

        try:
            resp = requests.post("https://api.labellamafia.com.br:9443/api/totvsmoda/person/v2/legal-entities/search",data=body,headers=self.__get_header())
            if resp.status_code==200:
                return json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
            else:
                print("Erro: "+urllib.parse.unquote(resp.text))
        except requests.exceptions.RequestException as e:
            print("Erro em ERP.customer_list: " +format(e))
            pass
        pass


    def orders_list_today(self,_page:int = 1)->str | None:
        """Metodo que lista todos os pedidos do dia do ERP
        
        Args:
            _page (int, optional): pagina de registros. Defaults to 1.
            
        Returns:
            str | None: Objeto JSON ou Nada
        """
        try:
            body = """{
                    \"filter\":{
                        \"startOrderDate\": \""""+datetime.strftime("%Y-%m-%d")+"""T00:00:00.000Z\",
                        \"endOrderDate\": \""""+datetime.strftime("%Y-%m-%d")+"""T23:59:59.000Z\",
                        \"branchCodeList\": [1],
                        \"classifications\": [{
                            \"type\": 1,
                            \"codeList\": [\"1\",\"2\",\"4\",\"5\",\"13\",\"17\"]
                        }]
                    },
                    \"page\":"""+str(_page)+"""
                }"""

            resp = requests.post("https://api.labellamafia.com.br:9443/api/totvsmoda/sales-order/v2/orders/search",data=body,headers=self.__get_header())

            if resp.status_code == 200:
                return json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
            else:
                print("Erro: "+urllib.parse.unquote(resp.text))
        except requests.exceptions.RequestException as e:
            print("Erro em ERP.order_list_today")
            pass
        return None


    def order_list_by_customer(self,_page:int = 1,_customer:str="")->str | None:
        """Metodo que lista todos os pedidos do cliente do ultimo ano
        
        Args:
            _page (int, optional): pagina de registros. Defaults to 1.
            _customer(string,optional): cpf ou cnpj do cliente. Defaults to ""
            
        Returns:
            str | None: Objeto JSON ou Nada
        """
        try:
            body = """{
                \"filter\":{
                    \"startOrderDate\": \""""+(datetime.now()+timedelta(days=-365)).strftime("%Y")+"""-01-01\",
                    \"endOrderDate\": \""""+datetime.now().strftime("%Y-%m-%d")+"""\",
                    \"customerCpfCnpjList\": [\""""+_customer+"""\"],
                    \"branchCodeList\":[1]
                },
                \"expand\": \"classifications\",
                \"page\": """+str(_page)+""",
                \"pageSize\":500
            }"""
            resp = requests.post("https://api.labellamafia.com.br:9443/api/totvsmoda/sales-order/v2/orders/search",data=body,headers=self.__get_header())
            if resp.status_code == 200:
                return json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
            else:
                print("Erro: "+urllib.parse.unquote(resp.text))
        except requests.exceptions.RequestException as e:
            print("Erro em ERP.order_list_by_customer")
            pass
        return None


    def order_get_by_number(self,_number:str)->str | None:
        """Metodo que obtem um pedido atraves do numero
        
        Args:
            _number(string): numero do pedido.
            
        Returns:
            str | None: Objeto JSON ou Nada
        """
        try:
            body = """{
                \"filter\":{
                    \"branckCodeList\": [1],
                    \"orderCodeList\":["""+_number+"""]
                }
            }"""
            resp = requests.post("https://api.labellamafia.com.br:9443/api/totvsmoda/sales-order/v2/orders/search",data=body,headers=self.__get_header())
            if resp.status_code == 200:
                return json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
            else:
                print("Erro: "+urllib.parse.unquote(resp.text))
        except requests.exceptions.RequestException as e:
            print("Erro em ERP.order_get")
            pass

        return None


    def order_get_by_customer_today(self,_customer:str)->str | None:
        """Metodo que lista todos os pedidos do cliente do dia
        
        Args:
            _number(string): numero do pedido.
            
        Returns:
            str | None: Objeto JSON ou Nada
        """
        try:
            body = """{
                \"filter\":{
                    \"startOrderDate\": \""""+(datetime.now()+timedelta(days=-30)).strftime("%Y-%m-%d")+"""\",
                    \"endOrderDate\": \""""+datetime.now().strftime("%Y-%m-%d")+"""\",
                    \"customerCpfCnpjList\": [\""""+_customer+"""\"],
                    \"branchCodeList\":[1]
                },
                \"expand\": \"classifications\"
            }"""
            resp = requests.post("https://api.labellamafia.com.br:9443/api/totvsmoda/sales-order/v2/orders/search",data=body,headers=self.__get_header())
            if resp.status_code == 200:
                return json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
            else:
                print("Erro: "+urllib.parse.unquote(resp.text))
        except requests.exceptions.RequestException as e:
            print("Erro em ERP.order_get_by_customer_today")
            pass
        return None

    def representative_list(self,_page:int = 1) -> str | None:
        """Metodo que lista todos os representantes do ERP
        
        Args:
            _page (int, optional): pagina de registros. Defaults to 1.
            
        Returns:
            str | None: Objeto JSON ou Nada
        """
        try:
            body = """{
                    \"filter\":{
                        \"representativeCodeList\":["""+self.config.get().erp.representatives+"""]
                    },
                    \"expand\": \"customers\",
                    \"page\":"""+str(_page)+""",
                    \"pageSize\": 500
                }"""

            resp = requests.post("https://api.labellamafia.com.br:9443/api/totvsmoda/person/v2/representatives/search",data=body,headers=self.__get_header())

            if resp.status_code == 200:
                return json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
            else:
                print("Erro: "+urllib.parse.unquote(resp.text))
        except requests.exceptions.RequestException as e:
            print("Erro em ERP.representative_list")
            pass
        return None


    def find_customer(self,_cnpj:str) -> str | None:
        """Metodo que lista todos os representantes do ERP
        
        Args:
            _page (int, optional): pagina de registros. Defaults to 1.
            
        Returns:
            str | None: Objeto JSON ou Nada
        """
        try:
            body = """{
                    \"filter\":{
                        \"cnpjList\":[\""""+_cnpj+"""\"]
                    },
                    \"expand\": \"phones,addresses,emails\",
                    \"pageSize\": 500
                }"""

            resp = requests.post("https://api.labellamafia.com.br:9443/api/totvsmoda/person/v2/legal-entities/search",data=body,headers=self.__get_header())

            if resp.status_code == 200:
                return json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
            else:
                print("Erro: "+urllib.parse.unquote(resp.text))
        except requests.exceptions.RequestException as e:
            print("Erro em ERP.find_customer")
            pass
        return None