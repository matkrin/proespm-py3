import os
import json
from dataclasses import dataclass


@dataclass
class Config:
    mode:str
    use_labjournal: bool
    path_data: str
    path_labjournal: str
    save_stm_pngs: bool
    path_report_out: "str"


try:
    config_file = os.path.join(
        os.path.join(os.path.dirname(__file__), ".."), "config.json"
    )
    
    with open(config_file) as f:
        config_dict = json.load(f)


    config = Config(**config_dict)
    
except FileNotFoundError:
    config = Config("folder-based", False, "", "", False, "")
    
    
# mode = config_dict["mode"]
# use_labjournal = config_dict["use_labjournal"]
# path_data = config_dict["path_data"]
# path_labjournal = config_dict["path_labjournal"]
# save_stm_pngs = config_dict["save_stm_pngs"]
# path_report_out = config_dict["path_report_out"]
