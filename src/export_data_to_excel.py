import sys
from datetime import datetime
from os.path import dirname, abspath

from models import BTCUSDT_table_ORM
from queries.orm import select_data_orm
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt

from src.statistics import find_statistic, find_static_percent, find_levels, find_level_with_min_delta

sys.path.insert(0, dirname(dirname(abspath(__file__))))
from src.utils import predictable_price, parallel_line, trend_check, add_elem_series, add_last_elem_series, \
    create_trend, check_point_and_add_trends, check_point_and_trends

N = input('Введите N (30, 20, 10, 5, 1): ')
data = select_data_orm(BTCUSDT_table_ORM)

date = []
open_prise = []
close_prise = []
height_prise = []
low_prise = []
relative_height = []
relative_low = []

for elem in data:
    date.append(elem.date)
    open_prise.append(elem.open_prise)
    close_prise.append(elem.close_prise)
    height_prise.append(elem.height_prise)
    low_prise.append(elem.low_prise)
    relative_height.append(elem.characteristic.__dict__[f'relative_height_{N}'])
    relative_low.append(elem.characteristic.__dict__[f'relative_low_{N}'])

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
}
)
left, right = find_static_percent(data)
# # Определим цвет каждого бара
colors = ['y' if abs(open - close)/open*100 > right or abs(open - close)/open*100 < left else ('green' if low else ('red' if height else None)) for height, low, open, close in
          zip(df_base[f'relative_height'], df_base[f'relative_low'], df_base[f'Open'], df_base[f'Close'])]

# Определяем точки для линий сопротивлений
# seq_of_seq_of_points=[
#     [('2016-05-02',207),('2016-05-06',204)],
#     [('2016-05-10',208.5),('2016-05-19',203.5),('2016-05-25',209.5)],
#     [('2016-06-08',212),('2016-06-16',207.5)]
#     ]

resistance_lines = []
colors_resistance_lines = []
resistance_lines_extension = []
current_series = {'Trend_low': None,
                  'Trend_height': None,
                  'mother_low': None,
                  'mother_height': None,
                  'series_low': [],
                  'series_height': [],
                  'color_low': [],
                  'color_height': [],
                  'color': ''
                  }
# ----------------------------------------------------------------------------------------------------------------
# Создаём тунели в 3 этапа
for date, point_low, prise_low, point_height, prise_height in zip(date, df_base[f'relative_low'], low_prise,
                                                              df_base['relative_height'], height_prise):
    # print(date, point_low, point_height)
    # Создаём метеринские точки
    if point_low and not current_series['mother_low']:
        # print('создаём mother_low')
        current_series['mother_low'] = (str(date), prise_low)
        continue
    if point_height and not current_series['mother_height']:
        # print('создаём mother_height')
        current_series['mother_height'] = (str(date), prise_height)
        continue
    # Работа с локальным экстремумом, при условии, что он не принадлежит к главной трендовой линии или тренда вообще нет
    # Работа с локальным минимумом
    elif point_low and not current_series['Trend_low']:
        # Cоздаем тренд, если его не было
        if not current_series['Trend_height']:
            create_trend(current_series=current_series,
                         date=date,
                         prise_low=prise_low,
                         prise_height=prise_height,
                         position='low',
                         )
            continue
        # Проверяем, не нарушина ли структура
        if trend_check(current_series=current_series, new_prise=prise_low, position='low'):
            add_elem_series(current_series=current_series,
                            date=date,
                            prise_low=prise_low,
                            prise_height=prise_height,
                            position='low',
                            )
            continue
        # Структура была нарушена, очищаем последовательность и достраиваем теоретические линии к локальному эстремуму
        else:
            add_last_elem_series(current_series=current_series,
                                 date=date,
                                 prise_low=prise_low,
                                 prise_height=prise_height,
                                 resistance_lines=resistance_lines,
                                 colors_resistance_lines=colors_resistance_lines,
                                 position='low'
                                 )
            current_series = {'Trend_low': None,
                              'Trend_height': None,
                              'mother_low': (str(date), prise_low) if point_low else None,
                              'mother_height': (str(date), prise_height) if point_height else None,
                              'series_low': [],
                              'series_height': [],
                              'color_low': [],
                              'color_height': [],
                              'color': '', }
            continue
    # ----------------------------------------------------------------------------------------------------
    # #Работа с локальным максимумом
    elif point_height and not current_series['Trend_height']:
        # Cоздаем тренд, если его не было
        if not current_series['Trend_low']:
            create_trend(current_series=current_series,
                         date=date,
                         prise_low=prise_low,
                         prise_height=prise_height,
                         position='height',
                         )
            continue
        # Проверяем, не нарушена ли структура
        if trend_check(current_series=current_series, new_prise=prise_low, position='height'):
            add_elem_series(current_series=current_series,
                            date=date,
                            prise_low=prise_low,
                            prise_height=prise_height,
                            position='height',
                            )
            continue
        # Структура была нарушена, очищаем последовательность и достраиваем теоретические линии к локальному эстремуму
        else:
            add_last_elem_series(current_series=current_series,
                                 date=date,
                                 prise_low=prise_low,
                                 prise_height=prise_height,
                                 resistance_lines=resistance_lines,
                                 colors_resistance_lines=colors_resistance_lines,
                                 position='height'
                                 )
            current_series = {'Trend_low': None,
                              'Trend_height': None,
                              'mother_low': (str(date), prise_low) if point_low else None,
                              'mother_height': (str(date), prise_height) if point_height else None,
                              'series_low': [],
                              'series_height': [],
                              'color_low': [],
                              'color_height': [],
                              'color': '', }
            continue
    # ----------------------------------------------------------------------------------------------------
    # Проверяем на истинность low -> trends=low и добавляем новую точку, если истинна
    if check_point_and_add_trends(current_series, prise_low, prise_height, date, point_low, point_height):
        continue
    # ----------------------------------------------------------------------------------------------------
    # Происходит слом по система  low !-> trends=low добавляем последние линии и очищаем серию
    if point_height and not check_point_and_trends(current_series=current_series, position='height', point=point_height,
                                                   prise=prise_height) or \
            point_low and not check_point_and_trends(current_series=current_series, position='low', point=point_low,
                                                     prise=prise_low):
        # Добавляем 2 тестовых линии, которые показывают, что приломилось не так
        position = 'height' if point_low else 'low'
        add_last_elem_series(current_series=current_series,
                             date=date,
                             prise_low=prise_low,
                             prise_height=prise_height,
                             resistance_lines=resistance_lines,
                             colors_resistance_lines=colors_resistance_lines,
                             position=position
                             )

        current_series = {'Trend_height': None, 'Trend_low': None,
                          'mother_low': (str(date), prise_low) if point_low else None,
                          'mother_height': (str(date), prise_height) if point_height else None, 'series_low': [],
                          'series_height': [], 'color_low': [], 'color_height': []}
        continue
    #     Если мы дошли до сюда - значит это просто рядовой бар
    else:
        continue

mpf.plot(df, type='candle', marketcolor_overrides=colors,
         alines=dict(alines=resistance_lines, colors=colors_resistance_lines))
# ---------------------------------------------------------------------------------------------------------------

levels = find_levels(data)
print(len(levels))

# levels = list(find_level_with_min_delta(data))
#
# mpf.plot(df, type='candle', hlines=levels)

