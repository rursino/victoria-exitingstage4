import os
from core import CoronaStats

CURRENT_PATH = os.path.dirname(__file__)
DATA_DIR = CURRENT_PATH + "./../data/"

df = CoronaStats(DATA_DIR + 'net_cases.csv', 0.1)

print(df.date_to_trigger())