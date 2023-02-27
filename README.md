# rdstation-virtualage

## Integração entre o sistema Virtual Age e o CRM Rdstation


Todas as informações encontram-se no arquivo ``Config.json``


Realizar agendamento do script integracao.py apenas 1x no mês (as datas do calendário estão no config caso haja necessidade de alterações). 
Esse script executa sempre antes de entrar uma nova coleção.

Realizar agendamento do script pedidos.py diário (as datas das vendas seguem as do calendário e estão no config caso haja necessidade de alterações);
Esse script executa durante o período de vendas de uma coleção, já que trabalha a situação dos pedidos dentro do CRM.