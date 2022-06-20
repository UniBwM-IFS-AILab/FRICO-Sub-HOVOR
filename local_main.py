from time import sleep
import jsonpickle
from environment import initialize_local_environment
from hovor.configuration.json_configuration_provider import JsonConfigurationProvider
from hovor.core import run_interaction
from setup_hovor_rasa import setup_hovor_rasa
import subprocess
import requests
from requests.exceptions import ConnectionError

initialize_local_environment()

setup_hovor_rasa("pizza", train=False)
subprocess.Popen("./rasa_setup.sh", shell=True)

configuration_provider = JsonConfigurationProvider("./pizza/pizza")

# configuration_provider = JsonConfigurationProvider("./local_data/gold_standard_data/gold")

# test on recoded provider
json = jsonpickle.encode(configuration_provider)
configuration_provider = jsonpickle.decode(json)
configuration_provider.check_all_action_builders()

while True:
    try:
        requests.post('http://localhost:5005/model/parse', json={"text": "test"})
    except ConnectionError:
        sleep(0.1)
    else:
        break
run_interaction(configuration_provider)
