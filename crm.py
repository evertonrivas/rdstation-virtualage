from asyncio.windows_events import NULL
from tkinter.messagebox import NO
from config import TaskType
from crm_anotation import CrmAnotation
from crm_company import CrmCompany
from crm_contact import CrmContact
from crm_opportunity import CrmOpportunity
import requests
import json
from types import SimpleNamespace
import urllib.parse

from crm_task import CrmTask

class CRM():

    def __init__(self,_token:str) -> None:
        self.token = _token
        pass


    def __get_header(self)->str:
        return {
            "Content-Type":"application/json",
            "Accept":"*/*",
            "Accept-Encoding": "gzip,deflate,br",
            "Connection":"keep-alive"
        }


    def company_list(self,_page:int = 1) -> str | None:
        """Metodo que lista as empresas disponiveis no CRM

        Args:
            _page (int, optional): numero da pagina com os registros. Defaults to 1.

        Returns:
            str | None: objeto JSON ou Nada
        """
        resp = requests.get("https://crm.rdstation.com/api/v1/organizations?token="+self.token+"&page="+str(_page))

        if resp.status_code == 200:
            companies = json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
            if companies.total > 0:
                return companies
        return None


    def company_find_by_name(self,_query:str) -> str | None:
        """Metodo que busca uma empresa atraves do nome porque o CRM so permite buscar pelo nome

        Args:
            _query (str): texto contendo o nome da empres

        Returns:
            str | None: objeto JSON ou Nada
        """
        new_query = urllib.parse.quote(_query)
        resp = requests.get("https://crm.rdstation.com/api/v1/organizations?token="+self.token+"&q="+new_query)

        if resp.status_code == 200:
            companies = json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
            if companies.total > 0:
                for company in companies.organizations:
                    return company
        return None


    def company_get(self,_id_empresa:str) -> str | None:
        """Metodo que busca uma empresa pelo codigo

        Args:
            _id_empresa (str): codigo da empresa que existe no CRM

        Returns:
            str | None: objeto JSON ou Nada
        """
        resp = requests.get("https://crm.rdstation.com/api/v1/organizations/"+_id_empresa+"?token="+self.token)
        if resp.status_code == 200:
            return json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
        return None
    

    def company_save(self, _company: CrmCompany, _company_id:str = "") -> str | None:
        """Metodo que salva uma nova empresa no CRM

        Args:
            _company (CrmCompany): Objeto que formata a empresa para envio
            _company_id (str, optional): id da empresa (serve em caso de atualizacao). Defaults to "".

        Returns:
            str | None: objeto JSON ou Nada
        """
        if _company_id=="":
            url = "https://crm.rdstation.com/api/v1/organizations?token="+self.token
        else:
            url = "https://crm.rdstation.com/api/v1/organizations/"+_company_id+"?token="+self.token

        resp = requests.post(url, data= _company.get_json_format(),headers=self.__get_header())
        if resp.status_code == 200:
            return json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
        else:
            print("Erro ao salvar empresa: "+str(resp.status_code)+" - "+resp.text)
            #print(_company.get_json_format())
        return False
    
    
    def contact_list(self,_page:int = 1) -> str | None:
        """Metodo que lista as empresas existentes no CRM

        Args:
            _page (int, optional): pagina contendo os registros. Defaults to 1.

        Returns:
            str | None: objeto JSON ou Nada
        """
        resp = requests.get("https://crm.rdstation.com/api/v1/contacts?token="+self.token+"&page="+str(_page))
        return None
      

    def contact_save(self, _contact: CrmContact, _contact_id:str = "") -> bool:
        """Metodo que salva um contado dentro do CRM

        Args:
            _contact (CrmContact): Objeto que formata o contato para salvar
            _contact_id (str, optional): id do contato (serve em caso de atualizacao). Defaults to "".

        Returns:
            bool: verdadeiro ou falso
        """
        if _contact_id=="":
            url = "https://crm.rdstation.com/api/v1/contacts?token="+self.token
        else:
            url = "https://crm.rdstation.com/api/v1/contacts/"+_contact_id+"?token="+self.token
            resp = requests.post(url,data=_contact.get_json_format(False),headers=self.__get_header())
            if resp.status_code==200:
                return True
        return False

    
    def opportunity_list(self,_page:int = 1,_deal_stage_id:str = "") -> str | None:
        """Metodo que realiza a listagem de oportunidades disponiveis no CRM para um determinado estagio do funil ou nao.
           Sao listadas 200 oportunidades em cada busca

        Args:
            _page (int, optional): pagina de registros. Defaults to 1.
            _deal_stage_id (str, optional): codigo do estagio do funil. Defaults to "".

        Returns:
            _type_: objeto JSON ou Nada
        """
        url = "https://crm.rdstation.com/api/v1/deals?token="+self.token+"&page="+str(_page)+"&limit=200"
        
        if _deal_stage_id != "": url += "&deal_stage_id="+_deal_stage_id

        resp = requests.get(url)
        if resp.status_code==200:
            deals = json.loads(resp.text,object_hook=lambda d:SimpleNamespace(**d))
            if deals.total > 0:
                return deals
        return None

    def opportunity_get(self,_opportunity_id:str) ->str | None:
        url = "https://crm.rdstation.com/api/v1/deals/"+_opportunity_id+"?token="+self.token

        resp = requests.get(url)
        if resp.status_code==200:
            return json.loads(resp.text,object_hook=lambda d:SimpleNamespace(**d))
        return None


    def opportunity_save(self, _oportunity: CrmOpportunity, _oportunity_id:str = "") -> str | bool:
        """Metodo que salva uma oportunidade

        Args:
            _oportunity (CrmOpportunity): Objeto que formata a oportunidade para salvar
            _oportunity_id (str, optional): id da oportunidade (serve para atualizar o registro). Defaults to "".

        Returns:
            str | bool: objeto JSON ou false
        """
        if _oportunity_id=="":
            url = "https://crm.rdstation.com/api/v1/deals?token="+self.token
        else:
            url = "https://crm.rdstation.com/api/v1/deals/"+_oportunity_id+"?token="+self.token

        resp = requests.put(url,data = _oportunity.get_json_format(),headers=self.__get_header())
        if resp.status_code == 200:
            return json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
        else:
            print("Erro ao salvar oportunidade: "+_oportunity_id+"\n\n"+_oportunity.get_json_format()+"\n\n"+resp.status_code+"\n\n"+resp.text)
        return False

    
    def funil_deals(self,_funil_id:str = "")->str | None:
        """Metodo que salva uma oportunidade

        Args:
            _oportunity (CrmOpportunity): Objeto que formata a oportunidade para salvar
            _oportunity_id (str, optional): id da oportunidade (serve para atualizar o registro). Defaults to "".

        Returns:
            str | bool: objeto JSON ou false
        """
        if _funil_id=="":
            url = "https://crm.rdstation.com/api/v1/deal_pipelines?token="+self.token
            #url = "https://crm.rdstation.com/api/v1/deals?token="+self.token
        else:
            url = "https://crm.rdstation.com/api/v1/deal_pipelines/"+_funil_id+"?token="+self.token
            #url = "https://crm.rdstation.com/api/v1/deals/"+_oportunity_id+"?token="+self.token

        resp = requests.get(url,headers=self.__get_header())
        if resp.status_code == 200:
            return json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
        else:
            print("Erro ao salvar oportunidade: "+str(resp.status_code)+" - "+resp.text)
            #print(_oportunity.get_json_format())
        return False


    def anotation_create(self, _anotation: CrmAnotation) -> bool:
        """Metodo que cria uma nova anotacao no CRM

        Args:
            _anotation (CrmAnotation): Objeto que formata a anotacao para salvar

        Returns:
            bool: verdadeiro ou falso
        """
        resp = requests.post("https://crm.rdstation.com/api/v1/activities?token="+self.token, data=_anotation.get_json_format(),headers={"Content-Type":"application/json","Accept":"*/*","Accept-Encoding": "gzip,deflate,br","Connection":"keep-alive"})
        if resp.status_code == 200:
            return True
        else:
            print("Erro ao salvar anotacao: "+str(resp.status_code)+" - "+resp.text)
            #print(_anotation.get_json_format())
        return False


    def task_list(self,_page:int = 1,_deal_stage_id:str = "",_type:TaskType = NULL,_user_id:str = "",_date_start:str = "", _date_end:str = "") -> str | None:
        """Metodo que lista uma ou mais tarefas do CRM

        Args:
            _page (int, optional): pagina de registros. Defaults to 1.
            _deal_stage_id (str, optional): codigo do estagio do funil de vendas. Defaults to "".
            _type (TaskType, optional): tipo da tarefa. Defaults to NULL.
            _user_id (str, optional): codigo do usuario que eh dono da tarefa. Defaults to "".
            _date_start (str, optional): data de inicio dos registros (formato AAAA-MM-DD). Defaults to "".
            _date_end (str, optional): data final dos registros (formato AAAA-MM-DD). Defaults to "".

        Returns:
            str | None: objeto JSON ou Nada
        """
        url = "https://crm.rdstation.com/api/v1/tasks?token="+self.token+"&page="+str(_page)

        if _deal_stage_id!="": url +="&deal_stage_id="+_deal_stage_id
        if _type!=NULL: url +="&ltype="+_type
        if _user_id!="": url += "&user_id ="+_user_id
        if _date_start!="":
            if _date_end!="":
                url += "&date_start="+_date_start+"&date_end="+_date_end

        resp = requests.get(url)
        if resp.status_code == 200:
            return json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
        return None


    def task_create(self,_task:CrmTask) -> bool:
        """Metodo que cria uma nova tarefa no CRM

        Args:
            _task (CrmTask): Objeto que formata a tarefa para salvar

        Returns:
            bool: verdadeiro ou falso
        """
        try:
            resp = requests.post("https://crm.rdstation.com/api/v1/tasks?token="+self.token, data=_task.get_json_format(),headers={"Content-Type":"application/json","Accept":"*/*","Accept-Encoding": "gzip,deflate,br","Connection":"keep-alive"})
            if resp.status_code == 200:
                return True
            else:
                print("Erro ao salvar tarefa: "+str(resp.status_code)+" - "+resp.text)
                print(_task.get_json_format())
        except Exception as e:
            print(e.__str__())
            
        return False


    def source_value_to_id(self,value:int)->str:
        """Funcao que converte o texto em id do campo fonte

        Args:
            value (str): Codigo do valor do campo

        Returns:
            str: _description_
        """
        if value==75413:
            return '63c0386a19e4a50015433c65' #Andres
        if value==16803:
            return '63c03871479fcf001265b34a' #Arildo
        if value==82466:
            return '63c0387b31e80800118a8f26' #Danilo
        if value==79759:
            return '63c03887c150e90018495ecf' #Diego Castilho
        if value==80008:
            return '63c03880cf19e1000fe8da4a' #Diego
        if value==81975:
            return '63c0388c8ea7c70018f30930' #Dinho
        if value==81973:
            return '63c03892719c3f000b2b2aba' #Edval
        if value==71793:
            return '63c0389c9abc020022d2a153' #Felipe
        if value==14336:
            return '63c038a1cf19e1001ce8d995' #Gustavo
        if value==91171:
            return '63c03b79479fcf000c65b7f2' #Junior
        if value==20:
            return '63c038ad9cb198000d93528f' #Loureiro
        if value==75717:
            return '63c038b4c150e9000c496004' #Marcus
        if value==78318:
            return '63c038b8a885fc00177996b4' #Maycon
        if value==71668:
            return '63c038c0cf19e1000be8dd34' #Pedro
        if value==17:
            return '63c038c52e944200166f8cb5' #Rezende
        if value==5021:
            return '63c038cc719c3f00262b2bba' #Rhannyer
        if value==82496:
            return '63c038d04b034400178d23a8' #Silvana
        if value==91172:
            return '63c03b73479fcf001865b73d' #Janio

    def get_opportunities_fields(self)->str | None:
        """Metodo que lista todos os campos existentes nas oportunidades

        Returns:
            str | None: Objeto json ou nada
        """

        url = "https://crm.rdstation.com/api/v1/custom_fields?token="+self.token+"&for=deal"

        resp = requests.get(url)
        if resp.status_code == 200:
            return json.loads(resp.text,object_hook=lambda d: SimpleNamespace(**d))
        return None