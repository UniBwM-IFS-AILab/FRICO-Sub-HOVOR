import requests
import json

from hovor.actions.action_base import ActionBase
from hovor import DEBUG


class WebPlansAction(ActionBase):
    """Web (i.e., REST API) type of action."""

    def __init__(self, *args):
        super().__init__(*args)

        self.url = self.config["call"]["endpoint"]
        field_values = self.context._fields
        self.post_payload = dict(self.config["call"]["default_payload"])
        with open ("dump.json", "w") as f:

            json.dump(field_values,f)
        #self.post_payload.update({"field_values": field_values})

        # for posted_context_variable in self.config["posted_context_variables"]:
        #     value = self.context.get_field(posted_context_variable)
        #     self.post_payload[posted_context_variable] = value

        self.is_external = False
        self._utterance = None

    def _start_execution_callback(self, action_result):

        # HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

        # DEBUG(f"\t calling {self.url}")
        # DEBUG(f"\t payload {self.post_payload}")
        try: 
            r = requests.post(self.url,  json=self.post_payload)
            DEBUG(f"\t {r.status_code} {r.reason}")

            
            data = json.loads(r.text)
            # print(data)
            self._utterance = data
            action_result.set_field("suceeded", True)
            action_result.set_field("type", "message")
            action_result.set_field("msg", self._utterance)
        
        except : 
            action_result.set_field("suceeded", False)
            action_result.set_field("type", "message")
            action_result.set_field("msg", " Generating plan for this scenario")
             
            # print("cannot")
        

    def _end_execution_callback(self, action_result, info):
        action_result.set_field("input", info)

