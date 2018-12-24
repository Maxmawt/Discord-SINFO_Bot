# created by Sami Bosch on Thursday, 08 November 2018

# This script launches the necessary functions for the real bot

import json
from run import runbot
import os


config = '../config.json'
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, config)

with open(filename) as f:
    data = json.load(f)
runbot(data["Token"])
