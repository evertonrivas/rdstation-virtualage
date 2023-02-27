class CrmContact():

    def __init__(self) -> None:
        self.token = ""
        self.name  = ""
        self.title = ""
        self.url   = ""
        self.email = ""
        self.phone = ""
        self.deal  = 0
        self.custom_fields_id = []
        self.custom_fields_value = []
        pass
    
    def set_token(self,_token:str) -> None:
        self.token = _token
    
    def set_name(self,_name:str) -> None:
        self.name = _name
    
    def set_title(self,_title:str) -> None:
        self.title = _title
    
    def set_url(self,_url:str) -> None:
        self.url = _url
    
    def set_email(self,_email:str) -> None:
        self.email = _email
        
    def set_phone(self,_phone:str) -> None:
        self.phone = _phone
        
    def set_deal_id(self,_deal) -> None:
        self.deal = _deal
    
    def set_organization_id(self,_organization_id:str) -> None:
        self.organization_id = _organization_id
        
    def add_custom_field(self,_field_id,_field_value) -> None:
        self.custom_fields_id.append(_field_id)
        self.custom_fields_value.append(_field_value)
    
    def get_json_format(self,_isForOportunity:bool = True) -> str:
    
        if self.title!="":
            mytitle = "\"title\": \""+self.title+"\""
        else:
            mytitle = ""
            
        if self.email!="":
            myemail = "\"emails\": [{\"email\":\""+self.email+"\"}],"
        else:
            myemail = ""
            
        if self.phone!="":
            myphone = "\"phones\": [{\"phone\":\""+self.phone+"\"}],"
        else:
            myphone = ""
            
        if self.deal!=0:
            mydeal = "\"deal_ids\": [{"+self.deal+"}]"
        else:
            mydeal = ""
            
        if len(self.custom_fields_id) > 0:
            fields = []
            for c,v in zip(self.custom_fields_id,self.custom_fields_value):
                fields.append("""{\"custom_field_id\":\""""+c+"""\",\"value\":\""""+v+"""\"}""")
            ffields = ",".join(fields)
            mycustom_fields = ",\"contact_custom_fields\": ["+ffields+"]"
        else:
            mycustom_fields = ""

        if _isForOportunity==False:
            _json = """{
            \"token\": \""""+self.token+"""\",
            \"contact\":{
                \"name\": \""""+self.name+"""\",
                \"organization_id\": \""""+self.organization_id+"""\",
                """+mytitle+"""
                """+myemail+"""
                """+myphone+"""
                """+mydeal+"""
                """+mycustom_fields+"""
                \"legal_bases\": [{\"category\": \"communications\", \"type\": \"consent\", \"status\": \"granted\"}]
                }
            }"""
        else:
            _json = """\"name\": \""""+self.name+"""\",
                \"organization_id\": \""""+self.organization_id+"""\",
                """+mytitle+"""
                """+myemail+"""
                """+myphone+"""
                """+mydeal+"""
                """+mycustom_fields+"""
                \"legal_bases\": [{\"category\": \"communications\", \"type\": \"consent\", \"status\": \"granted\"}]"""
        return _json