
from asyncio.windows_events import NULL
from config import TaskType
import json

class CrmTask():
    def __init__(self) -> None:
        self.token   = ""
        self.user_id = []
        self.deal_id = ""
        self.subject = ""
        self.type    = NULL
        self.hour    = ""
        self.date    = ""
        self.note    = ""
        pass

    def set_token(self,_token:str) -> None:
        self.token = _token

    def set_deal(self,_deal_id:str) -> None:
        self.deal_id = _deal_id

    def add_user(self,_user_id:str) -> None:
        self.user_id.append(_user_id)

    def set_subject(self,_text:str) -> None:
        self.subject = _text.encode("utf-8").decode("latin_1")

    def set_type(self,_type:TaskType) -> None:
        self.type = _type

    def set_hour(self,_hour:str) -> None:
        self.hour = _hour

    def set_date(self,_date:str) -> None:
        self.date = _date

    def set_note(self,_note:str) -> None:
        self.note = _note

    def get_json_format(self) -> str:

        if len(self.user_id) > 0:
            myusers = ",".join(f'"{w}"' for w in self.user_id)
        else:
            myusers = ""

        return """{
            \"token\": \""""+self.token+"""\",
            \"task\":{
                \"deal_id\": \""""+self.deal_id+"""\",
                \"user_ids\": ["""+myusers+"""],
                \"subject\": \""""+self.subject.encode().decode('latin_1')+"""\",
                \"type\": \""""+self.type.value+"""\",
                \"hour\": \""""+self.hour+"""\",
                \"date\": \""""+self.date+"""\",
                \"notes\": \""""+self.note.encode().decode('latin_1')+"""\"
            }
        }
        """