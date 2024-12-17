import os
import sys
import uuid
from datetime import datetime, timedelta
import time
from typing import Callable, Optional, List, TypeVar

import numpy as np
from moviepy import ImageSequenceClip
from numpy.ma.core import clip
from os.path import dirname, abspath
import pandas as pd
from pandas import DataFrame
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.stats import skew

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from src.avg import avg, avg_body
from src.utils import color_anomalies, avg_lines, transfer_data_to_dict, find_max_and_min, find_body
from src.models import BTCUSDT_table_ORM, Base
from src.queries.orm import select_data_orm, select_data_by_date

FOLDER_PATH = 'images/video/'
INDENT = 0.2

DATE_START = datetime(2022, 10, 17, 3)
DATE_STOP = datetime(2024, 8, 15)

T = TypeVar('T', bound=Base)


def make_video(date_start: datetime, date_stop: datetime, path: str, name: Optional[str], indent: float = 0.2,
               clear: bool = False, model: T = BTCUSDT_table_ORM,
               callback: Optional[Callable[[datetime, str, float], None]] = None) -> None:
    """Функция создания видео изменения цены от времени
    Функция ничего не возвращает, только создаёт видео и фото (при необходимости) в указанной директории.
    Функция работает долго, расчётное время 1 мин на 100 баров. В дальнейшем постараюсь ускорить её.

    Args:
        date_start (datetime): Дата с которой начинается построение графиков.
        date_stop (datetime): Дата до которой строится график.
        name (Optional[str]): Имя под которым будет сохраняться вся информация.
        path (str): Путь к директории, гду будет храниться вся информация.
        indent (float): Отступ по оси y при построении графи ков.
        clear (bool): Параметр отвечает за очистку фотографий в директории, по умолчания False.
        model (T): Модель к которой отправляется запрос.
        callback (Optional[Callable[DataFrame, str, float], None]]): Функция обработки данных и создания
        графика matplotlib, принимает на вход список элементов записи из бд, путь сохранения и отступ, ничего не
        возвращает. Опциональный аргумент, при значении None, просто рисуются бары во времени.

    Returns:
        None - функция ничего не возвращает, а только создаёт видео и фото (опционально)

    """
    count = 0
    date_center = date_start

    FOLDER_PATH = path

    if name is None:
        name = uuid.uuid4()
    path = f'{path}{name}_'

    while date_center < date_stop:
        callback(date_center=date_center, path=f"{path}{count}", models=model, indent=indent)
        count += 1
        date_center += timedelta(days=1)

    # Получаем список файлов PNG
    image_files = [os.path.join(FOLDER_PATH, f) for f in os.listdir(FOLDER_PATH) if
                   f.endswith('.png') and f.split('/')[0].startswith(name)]
    print(image_files)
    image_files = sorted(image_files, key=lambda x: int(x.split('.')[0].split('/')[-1].split('_')[-1]))
    # Частота кадров
    fps = 1
    # Создайте видеоклип из последовательности изображений
    clip = ImageSequenceClip(image_files, fps=fps)

    # Экспортируйте видеоклип в файл
    clip.write_videofile(f'{FOLDER_PATH}{name}.mp4', codec='libx264')

    if clear:
        for file in image_files:
            os.remove(file)


def make_slide_default(date_center: datetime, path: str, indent: float, models: T) -> None:
    """Функция создания графика бар

    Args:
        date_center (datetime): Текущая дата.
        path (str): Путь к файлу.
        indent (float): Отступ по оси y при построении графиков.
        models (T): Модель к которой отправляется запрос.

    Returns:
        None - функция ничего не возвращает, а только создаёт фото

    """
    date_left = (date_center - timedelta(days=60))
    date_right = (date_center + timedelta(days=30))

    date_left_str = date_left.strftime('%Y-%m-%d %H:%M:%S')
    date_right_str = date_right.strftime('%Y-%m-%d %H:%M:%S')

    data = select_data_by_date(models, start=None, stop=date_center)
    data = transfer_data_to_dict(data)
    df = pd.DataFrame({
        "Open": data['open_prise'],
        "High": data['height_prise'],
        "Low": data['low_prise'],
        "Close": data['close_prise'],
    },
        index=data['date']
    )
    df.index.name = "Date"

    data_delta = select_data_by_date(models, start=date_left, stop=date_center)
    data_delta = transfer_data_to_dict(data_delta)
    max_, min_ = find_max_and_min(data_delta)

    delta_y = (max_ - min_) * indent / (2 - indent * 2)

    mpf.plot(df, xlim=(date_left_str, date_right_str), ylim=(min_ - 2 * delta_y, max_ + 2 * delta_y),
             type='candle', savefig=path)


def make_slide_statistic(date_center: datetime, path: Optional[str], indent: float, models: T) -> None:
    """Функция создания графика бар, и мат распределения размеров бар.

    Args:
        date_center (datetime): Текущая дата.
        path (Optional[str]): Путь к файлу.
        indent (float): Отступ по оси y при построении графиков.
        models (T): Модель к которой отправляется запрос.

    Returns:
        None - функция ничего не возвращает, а только создаёт фото

    """
    date_left = (date_center - timedelta(days=60))
    date_right = (date_center + timedelta(days=30))

    date_left_str = date_left.strftime('%Y-%m-%d %H:%M:%S')
    date_right_str = date_right.strftime('%Y-%m-%d %H:%M:%S')

    data = select_data_by_date(models, start=None, stop=date_center)
    data = transfer_data_to_dict(data)
    df = pd.DataFrame({
        "Open": data['open_prise'],
        "High": data['height_prise'],
        "Low": data['low_prise'],
        "Close": data['close_prise'],
    },
        index=data['date']
    )
    df.index.name = "Date"

    data_delta = select_data_by_date(models, start=date_left, stop=date_center)
    data_delta = transfer_data_to_dict(data_delta)
    max_, min_ = find_max_and_min(data_delta)

    delta_y = (max_ - min_) * indent / (2 - indent * 2)

    ws = [6, 2]
    hs = [2, 6]

    fig = plt.figure(figsize=(15.5, 6.8))
    gs = GridSpec(2, 2, figure=fig, width_ratios=ws, height_ratios=hs)

    ax1 = fig.add_subplot(gs[0, :])
    bodies = find_body(data['open_prise'], data['close_prise'])
    A = skew(bodies)
    if A > 0.5:
        color = 'g'
    elif A < -0.5:
        color = 'r'
    else:
        color = 'b'
    ax1.set_title(f'Мат распределение, A = {A}')
    plt.hist(bodies, color=color, bins=10)


    ax2 = fig.add_subplot(gs[1, :])
    ax2.set_title('Цена')

    if path:
        print('nj ')
        mpf.plot(df, xlim=(date_left_str, date_right_str), ylim=(min_ - 2 * delta_y, max_ + 2 * delta_y),
                 type='candle', ax=ax2)
        fig.savefig(path)
    else:
        result = mpf.plot(df, xlim=(date_left_str, date_right_str), ylim=(min_ - 2 * delta_y, max_ + 2 * delta_y),
                          type='candle', ax=ax2)


make_video(date_start=datetime(2022, 10, 17, 3),
           date_stop=datetime(2024, 8, 15, 3),
           path=FOLDER_PATH,
           indent=INDENT,
           name='exemple2',
           model=BTCUSDT_table_ORM,
           callback=make_slide_statistic,
           clear=True
           )

# make_slide_statistic(date_center=datetime(2022, 10, 18, 3),
#                      indent=0.2,
#                      models=BTCUSDT_table_ORM,
#                      path=None
#                      )
