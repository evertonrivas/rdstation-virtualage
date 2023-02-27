from datetime import datetime
import erp
from config import Config

def check_customer_deal(_orders)->str | None:
    classif = []
    #varre cada item para obter a classificacao
    for it in _orders.items:
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












_cfg = Config()
_cfg.open() #abre a configuracao

_erp = erp.ERP(_cfg) #cria o objeto do ERP
_erp.get_token() #obtem o token


orders = _erp.order_list_by_customer(1,"35107232000128")
#print(orders)
print(check_customer_deal(orders))