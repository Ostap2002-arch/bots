import sys
from datetime import datetime
from os.path import dirname, abspath

from models import BTCUSDT_table_ORM
from queries.orm import select_data_orm
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt

from src.statistics import find_statistic, find_static_percent

sys.path.insert(0, dirname(dirname(abspath(__file__))))
from src.utils import predictable_price, parallel_line, trend_check, add_elem_series, add_last_elem_series, \
    create_trend, check_point_and_add_trends, check_point_and_trends

N = input('Введите N для основной тенденции (30, 20, 10, 5, 1): ')
N_2 = input('Введите N для основной вспомогательной (30, 20, 10, 5, 1): ')
data = select_data_orm(BTCUSDT_table_ORM)

date = []
open_prise = []
close_prise = []
height_prise = []
low_prise = []
relative_height = []
relative_low = []
relative_height_N = []
relative_low_N = []

for elem in data:
    print(elem.characteristic.__dict__)
    date.append(elem.date)
    open_prise.append(elem.open_prise)
    close_prise.append(elem.close_prise)
    height_prise.append(elem.height_prise)
    low_prise.append(elem.low_prise)
    relative_height.append(elem.characteristic.__dict__[f'relative_height_{N}'])
    relative_low.append(elem.characteristic.__dict__[f'relative_low_{N}'])
    relative_height_N.append(elem.characteristic.__dict__[f'relative_height_{N_2}'])
    relative_low_N.append(elem.characteristic.__dict__[f'relative_low_{N_2}'])
df = pd.DataFrame({
    "Open": open_prise,
    "High": height_prise,
    "Low": low_prise,
    "Close": close_prise,
},
    index=date
)
df.index.name = "Date"

df_base = pd.DataFrame({
    "Open": open_prise,
    "High": height_prise,
    "Low": low_prise,
    "Close": close_prise,
    "relative_height": relative_height,
    "relative_low": relative_low,
    "relative_height_N": relative_height_N,
    "relative_low_N": relative_low_N,
}
)
left, right = find_static_percent(data)
# # Определим цвет каждого бара
colors = [None if left < abs((open - close)/open * 100) < right else 'c' for open, high, low, close in zip(df_base[f'Open'], df_base[f'High'], df_base[f'Low'], df_base[f'Close'])]
# colors = ['red' if low or height else ('c' if height_N or low_N else None) for height, low, height_N, low_N in
#           zip(df_base[f'relative_height'], df_base[f'relative_low'], df_base[f'relative_height_N'], df_base[f'relative_low_N'])]

# Определяем точки для линий сопротивлений
# seq_of_seq_of_points=[
#     [('2016-05-02',207),('2016-05-06',204)],
#     [('2016-05-10',208.5),('2016-05-19',203.5),('2016-05-25',209.5)],
#     [('2016-06-08',212),('2016-06-16',207.5)]
#     ]


mpf.plot(df, type='candle', marketcolor_overrides=colors)