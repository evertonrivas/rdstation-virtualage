from time import sleep
from config import Config, LogType
import logging
from logging.handlers import TimedRotatingFileHandler
import crm
import erp
from crm_opportunity import CrmOpportunity
from crm_task import CrmTask
from datetime import datetime,timedelta

def log_config(_cfg:Config) -> None:
    _cfg.open()
    hdler = TimedRotatingFileHandler(_cfg.get().log.pedidos,when="midnight",backupCount=_cfg.get().log.drop_days)
    logging.basicConfig(level=logging.DEBUG,handlers=[hdler],format="%(asctime)s:%(levelname)s:%(message)s")


def write_log(_log_message:str,_log_type:LogType) -> None:
    if _log_type==LogType.ERROR:
        logging.error(_log_message)

    if _log_type==LogType.INFO:
        logging.info(_log_message)

    if _log_type==LogType.WARNING:
        logging.info(_log_message)



#-----------------------------------INICIO DO PROGRAMA-----------------------------------#
#cria o objeto de log
_cfg = Config()
#abre o arquivo de log
log_config(_cfg)

hoje = int(datetime.now().strftime("%d%m"))
ini_p1 = int(_cfg.get().colecao.inicio_vendas1.replace("-",""))
fim_p1 = int(_cfg.get().colecao.fim_vendas1.replace("-",""))

ini_p2 = int(_cfg.get().colecao.inicio_vendas2.replace("-",""))
fim_p2 = int(_cfg.get().colecao.fim_vendas2.replace("-",""))

ini_p3 = int(_cfg.get().colecao.inicio_vendas3.replace("-",""))
fim_p3 = int(_cfg.get().colecao.fim_vendas3.replace("-",""))

ini_p4 = int(_cfg.get().colecao.inicio_vendas4.replace("-",""))
fim_p4 = int(_cfg.get().colecao.fim_vendas4.replace("-",""))


def check_missing_field(_crm:crm.CRM,opportunity,crm_deal):
    #verifica quantos campos customizados ha na oportunidade
    if len(opportunity.deal_custom_fields)==1:
        #adiciona o campo obrigatorio de comprou calcados
        for field in _crm.get_opportunities_fields():
            if field.id!=opportunity.deal_custom_fields[0].custom_field_id:
                if field.required == True:
                    if field.type=="option":
                        if field.label=="Comprou Calçados":
                            valor = "Não"
                        else:
                            valor = ""
                    else:
                        valor = "-"
                else:
                    valor=""
                crm_deal.add_custom_field(field.id,valor)

    #realiza ajuste nas oportunidades que nao tem o campo
    for deal_field in opportunity.deal_custom_fields:
        if deal_field.value is None:
            if deal_field.custom_field.type=="option":
                if deal_field.custom_field.label=="Comprou Calçados":
                    valor = "Não"
                if deal_field.custom_field.label=="Cliente pote de Ouro":
                    valor = "Não"
            else:
                valor = "-"
        else:
            if deal_field.custom_field.type=="option":
                if deal_field.custom_field.label=="Cliente pote de Ouro":
                    valor = "Não"
                else:
                    valor = deal_field.value
            else:
                valor = deal_field.value
        #print("adicionou novo campo! - "+deal_field.custom_field.label+":"+valor)
        crm_deal.add_custom_field(deal_field.custom_field_id,valor)

def check_exist_order_in_stage(_crm:crm.CRM,_erp:erp.ERP,crm_deal:str):
    page = 1
    opportunity_list = _crm.opportunity_list(page,crm_deal)
    while True:
        for active in opportunity_list.deals:
            company = _crm.company_get(active.organization.id)
            for org_field in company.organization_custom_fields:
                if org_field.custom_field_id == _cfg.get().crm.business.taxvat_field_id:
                    #obtem os pedidos realizados nos ultimos 30 dias
                    pedidos = _erp.order_get_by_customer_30today(org_field.value)
                    #verifica se ha pedidos
                    if pedidos.totalItems > 0:

                        #havendo pedidos troca a oportunidade de estagio
                        crm_deal = CrmOpportunity(_cfg)
                        #crm_deal.set_user(active.organization.user.id)
                        crm_deal.set_deal_stage(_cfg.get().crm.opportunity.deal_order_pending)

                        check_missing_field(_crm,active,crm_deal)

                        #salva os dados da oportunidade
                        if _crm.opportunity_save(crm_deal,active.id)!=False:
                            write_log("Oportunidade "+active.name+" trocada de estagio no CRM para Pedido Feito!",LogType.INFO)
                            print("Oportunidade "+active.name+" trocada de estagio no CRM para Pedido Feito!")
                        else:
                            print("Ocorreu um erro ao tentar salvar a oportunidade "+active.name+"\n\n"+crm_deal.get_json_format())
            #colocado slép para não gerar problemas no servidor
            sleep(1)
        if opportunity_list.has_more==False:
            break
        else:
            #incrementa a pagina
            page += 1
            #busca novamente os dados com a pagina nova
            opportunity_list = _crm.opportunity_list(page,crm_deal)

if (hoje>=ini_p1 and hoje<=fim_p1) or (hoje>=ini_p2 and hoje<=fim_p2) or (hoje>=ini_p3 or hoje<=fim_p3) or (hoje>=ini_p4 or hoje<=fim_p4) :

    #envia o token para a classe do CRM
    _crm = crm.CRM(_cfg.get().crm.token)


    #cria o objeto do ERP
    _erp = erp.ERP(_cfg)
    #obtem o token para acessar os dados do ERP
    _erp.get_token()

    #--------------------------------------------------------------------------------------------------------#
    # Busca tudo o que tem no CRM com pedido feito e compara com o que tem no ERP.

    # Se existir o pedido no ERP entao remove o cliente do funil e envia para o funil padrao.
    # Se nao encontrar no ERP pelo pedido informado, entao coloca uma tarefa e envia email para ser verificado


    print("SEGUNDA ETAPA - PRECISA DE VERIFICACAO DIARIA APOS O DE INTEGRACAO")
    print("==================================================================")


    # print("\n\nINICIANDO VALIDACAO DOS CLIENTES COM PEDIDO FEITO - POTE DE OURO")
    # print("================================================================")
    # #verifica se foi cadastrada a etapa do funil que conterah as oportunidades para verificacao
    # if _cfg.get().crm.opportunity.deal_order_done != "":

    #     #lista as empresas que fazem parte da etapa do funil
    #     companies_crm = _crm.opportunity_list(1,_cfg.get().crm.opportunity.deal_order_done)

    #     if companies_crm!=None:
    #         #varre cada oportunidade do funil para obter as informacoes
    #         for opportunity in companies_crm.deals:
    #             #obtem os dados do campo que contem o numero do pedido (este campo esta nas configuracoes)
    #             for field_crm in opportunity.deal_custom_fields:
    #                 #verifica se o numero do campo personalizado eh igual ao que esta nas configuracoes
    #                 if field_crm.custom_field_id==_cfg.get().crm.opportunity.custom_field_order:
    #                     #numero_pedido = field_crm.value
    #                     #obtem um pedido atraves do numero no ERP
    #                     pedido = _erp.order_get_by_number(field_crm.value)
    #                     if pedido!=None:

    #                         crm_deal = CrmOpportunity(_cfg)
    #                         crm_deal.set_deal_stage(_cfg.get().crm.opportunity.deal_order_pending)cls

    #                         check_missing_field(_crm,opportunity,crm_deal)
                            
    #                         write_log("Oportunidade "+opportunity.id+" trocada de estagio no CRM",LogType.INFO)
    #                         _crm.opportunity_save(crm_deal,opportunity.id)
    #                 else:
    #                     #se o numero do pedido for divergente, entao adiciona um evento de e-mail para o responsavel
    #                     #verificar o conteudo do campo
    #                     task = CrmTask()
    #                     task.token = _cfg.get().crm.token
    #                     task.user_id.append(opportunity.user.id)
    #                     task.deal_id = opportunity.id
    #                     task.subject = "Divergência no pedido do Cliente: "+opportunity.name
    #                     task.type = TaskType.EMAIL
    #                     task.hour = "10:00"
    #                     task.date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    #                     task.note = "Verificar o número do pedido registrado no CRM, pois não é compatível com o pedido registrado no ERP"
    #                     _crm.task_create(task)
    #                     write_log("Criado email para verificacao do numero do pedido que esta divergente na oportunidade "+opportunity.id,LogType.INFO)


    #print("\n\nINICIANDO VALIDACAO DOS ATIVOS")
    #print("==============================")
    #check_exist_order_in_stage(_crm,_erp,_cfg.get().crm.opportunity.deal_customer_active)
    #print("\n\nINICIANDO VALIDACAO DOS CHURN")
    #print("=============================")
    #check_exist_order_in_stage(_crm,_erp,_cfg.get().crm.opportunity.deal_customer_churn)
    #print("\n\nINICIANDO VALIDACAO DOS INATIVOS")
    #print("================================")
    #check_exist_order_in_stage(_crm,_erp,_cfg.get().crm.opportunity.deal_customer_inactive)



    print("\n\nINICIANDO VALIDACAO DOS CLIENTES COM PEDIDO PENDENTE - CARTEIRA DE CLIENTES")
    print("=============================================================================")

    #busca todos os clientes do estagio de pedido pendente da carteira de clientes
    page = 1
    opportunities = _crm.opportunity_list(page,_cfg.get().crm.opportunity.deal_order_pending)
    #opportunities = _crm.opportunity_list(page,"63c053310a9efb000b5df7bf") #pedido Aprovado
    #opportunities = _crm.opportunity_list(page,"63c053398514df001b55d7fa") #pedido Cancelado
    #opportunities = _crm.opportunity_list(page,"638e023e7b3e830015d1b939") #pedido Pendente
    
    liberadoParaFaturamento = 0
    parcialmenteAtendido    = 0
    atendido                = 0
    bloqueado               = 0
    cancelado               = 0
    emComposicao            = 0
    emAnalise               = 0

    while True:
        #verifica se o stage possui oportunidades
        if int(opportunities.total) > 0:
            #para cada oportunidade encontrada
            for opportunity in opportunities.deals:
                #obtem os dados da empresa
                company = _crm.company_get(opportunity.organization.id)
                #varre os campos customizados
                for org_field in company.organization_custom_fields:
                    #verifica a existencia do campo taxvat (CPF/CNPJ)
                    if org_field.custom_field_id == _cfg.get().crm.business.taxvat_field_id:
                        if org_field.value!=None:
                            #obtem os pedidos realizados nos ultimos 30 dias
                            pedidos = _erp.last_order_by_customer(org_field.value)
                            #verifica se ha pedidos
                            if pedidos.totalItems > 0:
                                for pedido in pedidos.items:
                                    #print(pedido.statusOrder)
                                    if pedido.statusOrder == "BillingReleased" or pedido.statusOrder=="PartiallyAnswered" or pedido.statusOrder=="Attended" or pedido.statusOrder=="InProgress":
                                        #move os pedidos para outro estagio (Pedido Aprovado)
                                        crm_deal = CrmOpportunity(_cfg)

                                        check_missing_field(_crm,opportunity,crm_deal)
                                        
                                        crm_deal.set_deal_stage(_cfg.get().crm.opportunity.deal_order_approved)
                                        write_log("Oportunidade "+opportunity.id+" trocada de estagio no CRM",LogType.INFO)
                                        print("Oportunidade "+opportunity.name+" trocada de estagio no CRM para Pedido Aprovado!")
                                        _crm.opportunity_save(crm_deal,opportunity.id)
                                    


                                    if pedido.statusOrder == "Canceled":
                                        #move os pedidos para outro estagio (Cancelado)
                                        crm_deal = CrmOpportunity(_cfg)

                                        check_missing_field(_crm,opportunity,crm_deal)

                                        crm_deal.set_deal_stage(_cfg.get().crm.opportunity.deal_order_canceled)
                                        write_log("Oportunidade "+opportunity.id+" trocada de estagio no CRM",LogType.INFO)
                                        print("Oportunidade "+opportunity.name+" trocada de estagio no CRM para Pedido Cancelado!")
                                        _crm.opportunity_save(crm_deal,opportunity.id)

                                    if pedido.statusOrder=="BillingReleased":
                                        liberadoParaFaturamento += 1
                                    
                                    if pedido.statusOrder == "PartiallyAnswered":
                                         parcialmenteAtendido += 1

                                    if pedido.statusOrder == "Attended":
                                         atendido += 1

                                    if pedido.statusOrder == "Blocked":
                                         bloqueado += 1

                                    if pedido.statusOrder == "Canceled":
                                         cancelado += 1

                                    if pedido.statusOrder == "InComposition":
                                         emComposicao += 1

                                    if pedido.statusOrder == "InAnalysis":
                                         emAnalise += 1
                                    #print("Oportunidade "+opportunity.name+" não mudou de estágio por que o pedido está como: "+pedido.statusOrder)
                        else:
                            print("Cliente "+opportunity.name+" sem CNPJ!")

        if bool(opportunities.has_more) == False:
            break
        else:
            page += 1
            opportunities = _crm.opportunity_list(page,_cfg.get().crm.opportunity.deal_order_pending)

print("Liberado p/ faturamento: "+str(liberadoParaFaturamento))
print("Parcialmente Atendido: "+str(parcialmenteAtendido))
print("Atendido: "+str(atendido))
print("Bloqueado: "+str(bloqueado))
print("Cancelado: "+str(cancelado))
print("Em composicao: "+str(emComposicao))
print("Em Analise: "+str(emAnalise))