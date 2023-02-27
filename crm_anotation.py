
from config import Config


class CrmAnotation():
    def __init__(self,_config:Config) -> None:
        self.token   = ""
        self.user_id = ""
        self.deal_id = ""
        self.text    = ""
        self.config  = _config
        pass

    def set_token(self,_token:str) -> None:
        self.token = _token

    def set_deal(self,_deal_id:str) -> None:
        self.deal_id = _deal_id

    def set_text(self,_text:str) -> None:
        self.text = _text.encode("utf-8").decode("latin_1")

    def get_json_format(self) -> str:
        return """{
            \"token\": \""""+self.token+"""\",
            \"activity\":{
                \"user_id\": \""""+self.config.get().crm.default_user+"""\",
                \"deal_id\": \""""+self.deal_id+"""\",
                \"text\": \""""+self.text+"""\"
            }
        }
        """