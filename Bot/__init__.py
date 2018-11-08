# created by Sami Bosch on Thursday, 08 November 2018

# This script launches the necessary functions for the real bot

import json
from run import runbot


with open('config.json') as f:
    data = json.load(f)
runbot(data["Token"])
