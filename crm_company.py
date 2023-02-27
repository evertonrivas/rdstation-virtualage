
from config import Config


class CrmCompany():    

    def __init__(self,_config:Config) -> None:
        self.token  = ""
        self.name   = ""
        self.resume = ""
        self.url    = ""
        self.segments = []
        self.custom_fields_id = []
        self.custom_fields_value = []
        self.config = _config
        pass
   
    def set_token(self,_token:str) -> None:
        self.token = _token
        
    def set_name(self,_name:str) -> None:
        self.name = _name
        
    def set_resume(self,_resume:str) -> None:
        self.resume = _resume
        
    def set_url(self,_url:str) -> None:
        self.url = str(_url)
        
    def add_segment(self,_segment_name) -> None:
        self.segments.append(_segment_name)
    
    def add_custom_field(self,_field_id,_field_value) -> None:
        self.custom_fields_id.append(_field_id)
        self.custom_fields_value.append(_field_value)
        
    def get_json_format(self) -> str:
        """Este metodo realiza a formatacao das informacoes da empresa no
            formato necessario ao metodo post
            
        Returns: 
            Json: json object
        """
        segm = "\",\"".join(self.segments)
        
        # realiza o looping atraves das duas arrays para conseguir juntar a informacao
        if len(self.custom_fields_id) > 0:
            fields = []
            for c,v in zip(self.custom_fields_id,self.custom_fields_value):
                fields.append("""{\"custom_field_id\": \""""+c+"""\",\"value":\""""+v+"""\"}""")
            
            ffields = ",".join(fields)       
            mycustom_fields = ",\"organization_custom_fields\": ["+ffields+"]"
        else:
            mycustom_fields = ""
        
        if self.resume!="":
            myresume = "\"resume\": \""+self.resume+"\","
        else:
            myresume = ""
            
        if self.url!="":
            myurl = "\"url\": \""+self.url+"\","
        else:
            myurl = ""
        
        return """{
            "token" : \""""+self.token+"""\",
            "organization" : {
                "name" : \""""+self.name+"""\",
                """+myresume+"""
                """+myurl+"""
                \"user_id\" : \""""+self.config.get().crm.default_user+"""\",
                \"organization_segments\": [\""""+segm+"""\"]
                """+mycustom_fields+"""
            }
        }"""
    
    def get_uf_name(self,_sigla:str) -> str:
        if _sigla=="AC": state = "AC - Acre"
        if _sigla=="AL": state = "AL - Alagoas"
        if _sigla=="AP": state = "AP - Amapá"
        if _sigla=="AM": state = "AM - Amazonas"
        if _sigla=="BA": state = "BA - Bahia"
        if _sigla=="CE": state = "CE - Ceará"
        if _sigla=="DF": state = "DF - Distrito Federal"
        if _sigla=="ES": state = "ES - Espírito Santo"
        if _sigla=="GO": state = "GO - Goiás"
        if _sigla=="MA": state = "MA - Maranhão"
        if _sigla=="MT": state = "MT - Mato Grosso"
        if _sigla=="MS": state = "MS - Mato Grosso do Sul"
        if _sigla=="MG": state = "MG - Minas Gerais"
        if _sigla=="PA": state = "PA - Pará"
        if _sigla=="PB": state = "PB - Paraíba"
        if _sigla=="PR": state = "PR - Paraná"
        if _sigla=="PE": state = "PE - Pernambuco"
        if _sigla=="PI": state = "PI - Piauí"
        if _sigla=="RJ": state = "RJ - Rio de Janeiro"
        if _sigla=="RN": state = "RN - Rio Grande do Norte"
        if _sigla=="RS": state = "RS - Rio Grande do Sul"
        if _sigla=="RO": state = "RO - Rondônia"
        if _sigla=="RR": state = "RR - Roraima"
        if _sigla=="SC": state = "SC - Santa Catarina"
        if _sigla=="SP": state = "SP - São Paulo"
        if _sigla=="SE": state = "SE - Sergipe"
        if _sigla=="TO": state = "TO - Tocantins"
        return state.encode().decode("latin_1")

    def get_uf_region(self,_sigla:str) -> str:
        if _sigla=="AC" or _sigla=="AM" or _sigla=="RO" or _sigla=="RR" or _sigla=="PA" or _sigla=="AP" or _sigla=="TO": return "Norte"     
        if _sigla=="MA" or _sigla=="PI" or _sigla=="CE" or _sigla=="RN" or _sigla=="PB" or _sigla=="PE" or _sigla=="AL" or _sigla=="SE" or _sigla=="BA": return "Nordeste"
        if _sigla=="MT" or _sigla=="MS" or _sigla=="GO" or _sigla=="DF": return "Centro-Oeste"
        if _sigla=="ES" or _sigla=="MG" or _sigla=="RJ" or _sigla=="SP": return "Sudeste"
        if _sigla=="SC" or _sigla=="PR" or _sigla=="RS": return "Sul"