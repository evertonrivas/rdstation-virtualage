from config import Config
from crm_contact import CrmContact

class CrmOpportunity():
    

    def __init__(self,_config:Config) -> None:
        self.custom_fields_id = []
        self.custom_fields_value = []
        self.token         = ""
        self.name          = ""
        self.deal_stage_id = ""
        self.deal_source   = ""
        self.organization  = ""
        self.contact       = ""
        self.user_id       = ""
        self.config        = _config
        pass
    
    def set_name(self,_name:str) -> None:
        self.name = _name
    
    def set_deal_stage(self,_deal_stage_id:str) -> None:
        self.deal_stage_id = _deal_stage_id #etapa do funil
    
    def set_deal_source(self,_deal_source:str):
        self.deal_source = _deal_source #fonte da oportunidade (representantes)
    
    def add_custom_field(self,_field_id,_field_value) -> None:
        self.custom_fields_id.append(_field_id)
        self.custom_fields_value.append(_field_value)
        
    def set_organization_id(self,_organization_id:str) -> None:
        self.organization = _organization_id

    def set_contact(self,_contact:CrmContact) -> None:
        self.contact = _contact
    
    def set_user(self,_user) -> None:
        self.user_id = _user
    
    def get_json_format(self) -> str:
        # realiza o looping atraves das duas arrays para conseguir juntar a informacao
        mycustom_fields = ""
        #print("Tamanho dos campos: "+str(len(self.custom_fields_id)))
        if len(self.custom_fields_id) > 0:
            fields = []
            for c,v in zip(self.custom_fields_id,self.custom_fields_value):
                fields.append("""{ \"custom_field_id\": \""""+c+"""\",\"value\": \""""+v+"""\" }""")
            
            ffields = ",".join(fields)       
            mycustom_fields = ',\"deal_custom_fields\": ['+ffields+']'
          
        if self.deal_source!="":
            mysource = """,\"deal_source\":{ \"_id\": \""""+self.deal_source+"""\" }"""
        else:
            mysource = ""

        if self.contact!="":
            mycontact = """,\"contacts\":[{
                """+self.contact.get_json_format()+"""
            }],"""
        else:
            mycontact = ""

        if self.organization!="":
            myorganization = """,\"organization:\":{ \"_id\": \""""+self.organization+"""\" }"""
        else:
            myorganization = ""

        if self.name!="":
            myname = """\"name\": \""""+self.name+"""\","""
        else:
            myname = ""

        if self.deal_stage_id!="":
            mydeal = """,\"deal_stage_id\": \""""+self.deal_stage_id+"""\""""
        else:
            mydeal = ""

        return """{
            \"token\": \""""+self.config.get().crm.token+"""\",
            \"deal\": {
                """+myname+"""
                \"user\": {
                    \"_id\": \""""+self.user_id+"""\"
                }
                """+mycustom_fields+"""
            }
            """+mydeal+"""
            """+mycontact+"""
            """+mysource+"""
            """+myorganization+"""
        }"""