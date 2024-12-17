from datetime import datetime
from pybit.unified_trading import HTTP
import numpy as np

from models import BTCUSDT_table_day, BTCUSDT_table_ORM
#core
from queries.core import insert_info_table

#orm
from queries.orm import insert_info_table_orm


session = HTTP()

time_start = int(datetime(year=2022, month=10, day=16).timestamp() * 1000)
time_end = int((datetime(year=2024, month=8, day=16)).timestamp() * 1000)

print(f'Цена биткоина с {datetime.fromtimestamp(time_start / 1000)} по {datetime.fromtimestamp(time_end / 1000)}')
print('-'*100)


req = session.get_index_price_kline(
    category="inverse",
    symbol="BTCUSDT",
    interval='D',
    start=time_start,
    end=time_end,
    limit = 1000,
)

data = req['result']['list']
print(len(data))
data.reverse()
TABLE = BTCUSDT_table_day


for elem in data:
    date = datetime.fromtimestamp(int(elem[0]) / 1000)
    open_prise = float(elem[1])
    high_prise = float(elem[2])
    low_prise = float(elem[3])
    close_prise = float(elem[4])
    info_insert = {
        'date': date,
        'open_prise': open_prise,
        'close_prise': close_prise,
        'height_prise': high_prise,
        'low_prise': low_prise
    }

    insert_info_table_orm(BTCUSDT_table_ORM, **info_insert)



#
# data_old_close = list()
# data_old_time = list()
#
# period = 3
#
# data_avg = list()
# bollinger_band_high_values = list()
# bollinger_band_low_values = list()
#
# count = 0
# for d in data:
#     if len(data_old_close) < 3:
#         print('3')
#         data_old_time.append(float(d[0]))
#         data_old_close.append(float(d[4]))
#         bollinger_band_low_values.append(None)
#         bollinger_band_high_values.append(None)
#         continue
#     data_old_time.append(float(d[0]))
#     data_old_close.append(float(d[4]))
#
#     avg = np.mean(data_old_close[-period:])
#     st = np.std(data_old_close[-period:])
#
#     data_avg.append(avg)
#     bollinger_band_high_values.append((avg + 2 * st))
#     bollinger_band_low_values.append((avg - 2 * st))
# #     print(f'date - {datetime.fromtimestamp(int(data_old_time[-1])/1000)} avg - {avg}',
# #           f'bollinger_band_high_values - {bollinger_band_high_values[-1]}'
# #           f'bollinger_band_low_values - {bollinger_band_low_values[-1]}'  , sep='\n')
# #
# #     if data_old_close[-1] > bollinger_band_high_values[-1]:
# #         print('-'*50)
# #         print(f'Продажа в {datetime.fromtimestamp(int(data_old_time[-1])/1000)}')
# #         print('-' * 50)
# #         count += 1
# #     if data_old_close[-1] < bollinger_band_low_values[-1]:
# #         print('-' * 50)
# #         print(f'Покупка в {datetime.fromtimestamp(int(data_old_time[-1])/1000)}')
# #         print('-' * 50)
# #         count += 1
# #
# #
# # print(f'{count} из {len(data_young)}')
# # print(min())
#
#
# import sqlite3 as sq
# with sq.connect('test_data.sqlite') as con:
#     cur = con.cursor()
#     cur.execute("DROP TABLE btc")
#     cur.execute("""CREATE TABLE IF NOT EXISTS btc(
#         Time_open timestamp,
#         Open_prise REAL,
#         Height REAL,
#         Low REAL,
#         Close_prise REAL,
#         Color INT,
#         Bollinger_high REAL,
#         Bollinger_low REAL
#     )""")
#
#     for index, info in enumerate(data):
#         color = 1 if float(info[4]) - float(info[1]) >= 0 else 0
#         cur.execute("insert into btc values (?, ?, ?, ?, ?, ?, ?, ?)", (datetime.fromtimestamp(int(info[0])/1000),
#                                                                      *info[1:], color,
#                                                                      bollinger_band_high_values[index],
#                                                                      bollinger_band_low_values[index]))
#
#
#
#
