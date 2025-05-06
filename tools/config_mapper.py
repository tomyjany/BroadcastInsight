import box
from dotenv import load_dotenv
import os
import yaml

with open("config.yml", "r", encoding="utf8") as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))
load_dotenv()

def repeat():
    with open("config.yml", "r", encoding="utf8") as ymlfile:
        cfg = box.Box(yaml.safe_load(ymlfile))
    load_dotenv()
