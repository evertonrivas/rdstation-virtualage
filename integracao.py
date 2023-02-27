from asyncio import exceptions
from distutils.log import INFO
import logging 
from logging.handlers import TimedRotatingFileHandler
from time import sleep
from config import Config, LogType
import crm
from crm_anotation import CrmAnotation
from crm_company import CrmCompany
from crm_contact import CrmContact
from crm_opportunity import CrmOpportunity
import erp
from datetime import datetime

def log_config(_cfg:Config) -> None:
    _cfg.open()
    hdler = TimedRotatingFileHandler(_cfg.get().log.integracao,when="midnight",backupCount=_cfg.get().log.drop_days)
    logging.basicConfig(level=logging.DEBUG,handlers=[hdler],format="%(asctime)s:%(levelname)s:%(message)s")


def write_log(_log_message:str,_log_type:LogType) -> None:
    if _log_type==LogType.ERROR:
        logging.error(_log_message)

    if _log_type==LogType.INFO:
        logging.info(_log_message)

    if _log_type==LogType.WARNING:
        logging.info(_log_message)


def check_customer_deal(_orders)->str | None:
    classif = []
    #varre cada item para obter a classificacao
    for it in _orders:
        for cla in it.classifications:
            #verifica apenas em colecao global
            if cla.typeName=="COLECAO GLOBAL":
                #print(cla.name)
                if cla.name.find("INVERNO")!=-1 or cla.name.find("VERAO")!=-1:
                    name = cla.name.replace("LBM - ","").replace("LM - ","").replace("LM ","").replace("LBM ","").replace("1-","1").replace("2 -","2").replace("1 -","1")
                    if name.find("INVERNO")!=-1:
                        new_name = name[len(name)-4:len(name)]+" "+name[0:len("INVERNO 1 ")]
                    else:
                        new_name = name[len(name)-4:len(name)]+" "+name[0:len("VERAO 1 ")]
                    classif.append(new_name)
    classif = list(dict.fromkeys(classif))

    ano_atual = int(datetime.now().strftime("%Y"))
    ano_seguinte = ano_atual + 1

    comprou_ultima    = False
    comprou_penultima = False
    comprou_antepenultima = False
    #o ano foi dividido em 4 partes, em cada parte deve ter um tipo de verificacao

    #regra exclusiva para primeira carga do CRM
    if int(datetime.now().strftime("%m"))==1:
        for c in classif:
            if c.rstrip()==str(ano_atual)+" INVERNO 1":
                comprou_ultima = True
            if c.rstrip()==str(ano_atual)+" VERAO 2":
                comprou_penultima = True
            if c.rstrip()==str(ano_atual)+" VERAO 1":
                comprou_antepenultima = True


    #ateh marco deve ter a seguinte ordem:
    #ANO INVERNO 2
    #ANO INVERNO 1
    #ANO VERAO 2
    if int(datetime.now().strftime("%m"))==3:
        for c in classif:
            if c.rstrip()==str(ano_atual)+" INVERNO 2":
                comprou_ultima = True
            if c.rstrip()==str(ano_atual)+" INVERNO 1":
                comprou_penultima = True
            if c.rstrip()==str(ano_atual)+" VERAO 2":
                comprou_antepenultima = True

    #ateh junho deve ter a seguinte ordem:
    #ANO+1 VERAO 1
    #ANO INVERNO 2
    #ANO INVERNO 1
    if int(datetime.now().strftime("%m"))==6:
        for c in classif:
            if c.rstrip()==str(ano_seguinte)+" VERAO 1":
                comprou_ultima = True
            if c.rstrip()==str(ano_atual)+" INVERNO 2":
                comprou_penultima = True
            if c.rstrip()==str(ano_atual)+" INVERNO 1":
                comprou_antepenultima = True

    #ateh setembro deve ter a seguinte ordem:
    #ANO+1 VERAO 2
    #ANO+1 VERAO 1
    #ANO INVERNO 2
    if int(datetime.now().strftime("%m"))==9:
        for c in classif:
            if c.rstrip()==str(ano_seguinte)+" VERAO 2":
                comprou_ultima = True
            if c.rstrip()==str(ano_seguinte)+" VERAO 1":
                comprou_penultima = True
            if c.rstrip()==str(ano_atual)+" INVERNO 2":
                comprou_antepenultima = True

    #ateh dezembro deve ter a seguinte ordem:
    #ANO+1 INVERNO 1
    #ANO+1 VERAO 2
    #ANO+1 VERAO 1
    if int(datetime.now().strftime("%m"))==12:
        for c in classif:
            if c.rstrip()==str(ano_seguinte)+" INVERNO 1":
                comprou_ultima = True
            if c.rstrip()==str(ano_seguinte)+" VERAO 2":
                comprou_penultima = True
            if c.rstrip()==str(ano_seguinte)+" VERAO 1":
                comprou_antepenultima = True
    
    if comprou_ultima==True and comprou_penultima==True:
        return "ACTIVE"
    if comprou_ultima==False and comprou_penultima==True:
        return "CHURN"
    if comprou_ultima==True and comprou_penultima==False:
        return "CHURN"
    if comprou_antepenultima==True:
        return "INACTIVE"
    if comprou_antepenultima==False and comprou_ultima==False and comprou_antepenultima==False:
        return "INACTIVE"



#-----------------------------------INICIO DO PROGRAMA-----------------------------------#
#cria o objeto de log
_cfg = Config()
#abre o arquivo de log
log_config(_cfg)


#verifica se estah no momento de executar (antes de iniciar uma colecao jah que 'zera' a situaco dos clientes)

hoje = datetime.now().strftime("%d-m%")
if hoje==_cfg.get().colecao.periodo1 or hoje==_cfg.get().colecao.periodo2 or hoje==_cfg.get().colecao.periodo3 or hoje==_cfg.get().colecao.periodo4:

    #envia o token para a classe do CRM
    _crm = crm.CRM(_cfg.get().crm.token)


    #------------------------------------------------------------------------------------------#
    # Busca tudo o que tem no ERP e compara se a empresa existe no CRM. Se nao estiver no CRM
    # realiza o input dos dados como uma oportunidade usando o segundo funil de vendas comercial

    #cria o objeto do ERP
    _erp = erp.ERP(_cfg)
    #obtem o token para acessar os dados do ERP
    _erp.get_token()

    #contador para exibir na tela
    _clientes = 1

    print("ETAPA ERP => CRM")
    print("================")

    #busca todos os representantes
    representantes = _erp.representative_list()

    #varre cada representante
    for repres in representantes.items:
        print("\nRepresentante ("+str(repres.code)+"): "+repres.name+": Clientes: "+str(len(repres.customers))+"\n")
        #varre cada cliente associado ao representante
        for customer in repres.customers:
            #realiza a busca das informacoes do cliente no CRM
            empresa_crm = _crm.company_find_by_name(customer.name)

            #se o cliente nao for encontrado no CRM pelo nome entao ele serah criado
            if empresa_crm==None:
                cli = _erp.find_customer(customer.cpfCnpj)

                for cli_erp in cli.items:
                    #verifica se o cliente esta inativo no ERP
                    if cli_erp.status!="Inactive":

                        #monta o objeto empresa para receber os dados
                        crmCompany = CrmCompany(_cfg)
                        crmCompany.set_token(_cfg.get().crm.token)
                        crmCompany.set_name(str(cli_erp.name).encode().decode("latin_1"))
                        crmCompany.set_url(cli_erp.homePage)
                        crmCompany.add_segment('Moda')
                        crmCompany.add_custom_field(_cfg.get().crm.business.taxvat_field_id,cli_erp.cnpj) #CNPJ
                        crmCompany.add_custom_field(_cfg.get().crm.business.unit_field_id,_cfg.get().crm.default_business_unit) #Unidade de Negocio LBM/LM
                        
                        #verifica se no objeto do ERP existe endereco cadastrado
                        for addr_erp in cli_erp.addresses:
                            if addr_erp.addressType=='Commercial':
                                crmCompany.add_custom_field(_cfg.get().crm.business.state_field_id, crmCompany.get_uf_name(addr_erp.stateAbbreviation)) #UF
                                crmCompany.add_custom_field(_cfg.get().crm.business.city_field_id,str(addr_erp.cityName).encode().decode('latin_1')) #Cidade
                                crmCompany.add_custom_field(_cfg.get().crm.business.region_field_id,crmCompany.get_uf_region(addr_erp.stateAbbreviation)) #Regiao

                        #se conseguiu salvar grava o contato e tambem abre o Deal
                        try:
                            #o retorno pode vir como False ou um objeto
                            retSaveCli = _crm.company_save(crmCompany)
                            if retSaveCli!=False:
                                #cria e salva as informacoes da oportunidade atrelado na empresa
                                deal = CrmOpportunity(_cfg)
                                deal.set_name(cli_erp.name)
                                deal.set_user(_cfg.get().crm.default_user)
                                deal.set_organization_id(retSaveCli._id)
                                deal.add_custom_field(_cfg.get().crm.business.origin_contact,_cfg.get().crm.default_contact_origin) #origem do contato

                                #codigo para setar os representantes
                                source_id = _crm.source_value_to_id(repres.code)
                                deal.set_deal_source(source_id)

                                #aqui verifica os ultimos 3 pedidos do cliente para verificar em qual estagio do funila o cliente entrarah
                                orders = _erp.order_list_by_customer(1,cli_erp.cnpj)
                                if orders.totalItems >= 2:
                                    #valida o status comercial do cliente
                                    result = check_customer_deal(orders.items)

                                    if result == "ACTIVE":
                                        deal.set_deal_stage(_cfg.get().crm.opportunity.deal_customer_active) #ativo
                                    if result == "CHURN":
                                        deal.set_deal_stage(_cfg.get().crm.opportunity.deal_customer_churn) #churn
                                    if result == "INACTIVE":
                                        deal.set_deal_stage(_cfg.get().crm.opportunity.deal_customer_inactive) #inativo
                                else:
                                    deal.set_deal_stage(_cfg.get().crm.opportunity.deal_customer_inactive) #joga como inativo se so tiver feito um pedido
                                
                                #fim da verificacao dos 3 ultimos pedidos do cliente                        
                                deal.set_user(_cfg.get().crm.default_user) #usuario padrao

                                #cria e salva as informacoes do contato para atrelar na oportunidade
                                crmContact = CrmContact()
                                crmContact.set_name('Contato do ERP')
                                crmContact.set_organization_id(retSaveCli._id)
                                for email_erp in cli_erp.emails:
                                    if email_erp.isDefault==True:
                                        crmContact.set_email(email_erp.email)
                                for phone_erp in cli_erp.phones:
                                    if phone_erp.isDefault==True:
                                        crmContact.set_phone(phone_erp.number)
                                
                                #define o contato
                                deal.set_contact(crmContact)
                                #salva a oportunidade
                                retSaveOportunity = _crm.opportunity_save(deal)

                                anota = CrmAnotation(_cfg)
                                anota.set_token(_cfg.get().crm.token)
                                anota.set_deal(retSaveOportunity._id)
                                anota.set_text("Importação realizada pelo sistema de integração")
                                _crm.anotation_create(anota)

                                
                                write_log("Empresa "+cli_erp.name+" - "+cli_erp.cnpj+", adicionada com sucesso no CRM!",LogType.INFO)
                                print(str(_clientes)+ ". Empresa "+cli_erp.name+" - "+cli_erp.cnpj+", adicionada com sucesso no CRM!")
                                _clientes += 1
                            else:
                                write_log("Não foi possível salvar as informações da empresa "+cli_erp.name+" - "+cli_erp.cnpj,LogType.ERROR)
                                print("Não foi possível salvar as informações da empresa "+cli_erp.name+" - "+cli_erp.cnpj)
                        except exceptions.InvalidStateError as e:
                            print(e.with_traceback)
                    else:
                        write_log("Empresa "+customer.name+" esta INATIVA no sistema ERP")
                        print(str(_clientes)+". Empresa "+customer.name+" estah como Inativa no ERP")
                        _clientes += 1
            else:
                #print("Empresa "+cli_erp.name+" já existe no crm. Serão atualizadas as informações de contato apenas.")
                write_log("Empresa "+customer.name+" já existe no crm. Serão atualizadas as informações de oportunidade.",LogType.INFO)
                print(str(_clientes)+". Empresa "+customer.name+" já existe no crm. Serão atualizadas as informações de oportunidade.")
                _clientes += 1

                #aqui precisa buscar os clientes que estao nas 3 oportunidades fixadas do comercial para Carteira de Clientes(Ativos, Churn, e Inativos)
                #para cada cliente existente, precisa buscar as informacoes do ERP de pedidos para comparar no inicio de cada colecao e realocar dentro
                #de cada posicao

                #-------------------------------------------------------------------------------------------------------------#
                #                                       INICIO EMPRESAS ATIVAS
                #-------------------------------------------------------------------------------------------------------------#
                ops_page = 1

                #busca exatamente o funil desejado
                funil = _crm.funil_deals(_cfg.get().crm.customer_pipeline)

                #varre todas as estapas existentes num funil especificoo
                for stage in funil.deal_stages:
                    #para cada etapa, obtem todas as oportunidades disponiveis
                    opportunities = _crm.opportunity_list(ops_page,stage.id)
                    #enquanto houver mais dados que nao soh os da pagina atual
                    while opportunities.has_more:
                        #obtem os dados de cada oportunidade
                        for opportunity in opportunities:
                            #obtem os dados da empresa
                            company = _crm.company_get(opportunity.organization.id)
                            #obtem o campo do CNPJ
                            for field in company.organization_custom_fields:
                                if field.custom_field_id==_cfg.get().crm.business.taxvat_field_id:

                                    deal = CrmOpportunity(_cfg)
                                    orders = _erp.order_list_by_customer(1,field.value)
                                    if orders.totalItems >= 2:
                                        #valida o status comercial do cliente
                                        result = check_customer_deal(orders.items)

                                        if result == "ACTIVE":
                                            deal.set_deal_stage(_cfg.get().crm.opportunity.deal_customer_active) #ativo
                                        if result == "CHURN":
                                            deal.set_deal_stage(_cfg.get().crm.opportunity.deal_customer_churn) #churn
                                        if result == "INACTIVE":
                                            deal.set_deal_stage(_cfg.get().crm.opportunity.deal_customer_inactive) #inativo
                                    else:
                                        deal.set_deal_stage(_cfg.get().crm.opportunity.deal_customer_inactive) #joga como inativo se so tiver feito um pedido

                                    #troca a oportunidade de lugar dentro do funil
                                    _crm.opportunity_save(deal,opportunity.id)
                        ops_page += 1
                        opportunities = _crm.opportunity_list(ops_page,stage.id)
        sleep(1)