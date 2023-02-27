from crm import CRM
from config import Config
from crm_report import CrmReport
import csv


cfg = Config()
cfg.open()

crm = CRM(cfg.get().crm.token)

f = open('relatorio.csv',"w",encoding="utf-8",newline='')
writer = csv.writer(f)

header = ['nome','unidade negocios','cpf_cnpj','marcas','instagram','uf','cidade','regiao','telefone/email','pote de ouro','numero pedido','estagio funil']

writer.writerow(header)

funil = crm.funil_deals(cfg.get().crm.customer_golden_pot)


#para cada etapa do funil
for deal in funil.deal_stages:
    print(deal.name)
    page_opt = 1
    while True:
        opportunities = crm.opportunity_list(page_opt,deal.id)
        #varre cada oportunidade
        try:
            for opportunity in opportunities.deals:
                try:
                    #obtem os dados de uma empresa que esta na oportunidade
                    company = crm.company_get(opportunity.organization.id)

                    report = CrmReport()
                    report.name = opportunity.name
                    report.deal = deal.name
                    for field in company.organization_custom_fields:
                        if field.custom_field_id=="636a9d86767f4c0011ca04f7":
                            report.instagram = field.value
                        if field.custom_field_id=="636a9d9a4e3cd8000fb067e0":
                            report.city = field.value
                        if field.custom_field_id=="636a9e87eada620026bcf5ad":
                            report.state = field.value
                        if field.custom_field_id=="638dfed471dc07000b2f7238":
                            report.business_unit = field.value
                        if field.custom_field_id=="636a9f35b50296000b70e09d":
                            report.region = field.value
                        if field.custom_field_id=="636a9f91eada620026bcf787":
                            report.brands = field.value
                        if field.custom_field_id=="638f366fb858e50015599cf4":
                            report.taxvat = field.value

                    #primeiro telefone que existir
                    try:
                        report.phone_num = company.contacts[0].phones[0].phone
                    except:
                        try:
                            report.phone_num = company.contacts[0].emails[0].email
                        except:
                            report.phone_num = ""

                    for ofield in opportunity.deal_custom_fields:
                        if ofield.custom_field_id == "639b585c44f5fb000c8967a8":
                            report.order_num = ofield.value
                        if ofield.custom_field_id == "63bdabc01ec0e400242a6cfa":
                            report.golden_pot = ofield.value             
                    
                    row = []
                    row.append(report.name)
                    row.append(report.business_unit)
                    row.append(report.taxvat)
                    row.append(report.brands)
                    row.append(report.instagram)
                    row.append(report.state)
                    row.append(report.city)
                    row.append(report.region)
                    row.append(report.phone_num)
                    row.append(report.golden_pot)
                    row.append(report.order_num)
                    row.append(report.deal)

                    writer.writerow(row)

                    del row
                except:
                    print(opportunity.name)


            #verifica se ha paginas, nao havendo interrompe o looping
            if opportunities.has_more==False:
                print("Terminou")
                break
            else:
                print(str(page_opt)+". Concluidos 200")
                page_opt += 1
        except:
            break

f.close()