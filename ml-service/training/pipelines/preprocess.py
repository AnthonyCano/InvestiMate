#file for preprocessing dataimport pandas as pd
import pandas as pd
from pathlib import Path

RAW_FILE = Path("training/data/raw/all_stocks.csv")

df = (pd.read_csv(RAW_FILE, parse_dates=["date"]))