import os
import json

config_file = os.path.join(
    os.path.join(os.path.dirname(__file__), '..'), 'config.json'
)

with open(config_file) as f:
    config = json.load(f)

use_labjournal = config['use_labjournal']
path_data = config['path_data']
path_labjournal = config['path_labjournal']
save_stm_pngs = config['save_stm_pngs']
