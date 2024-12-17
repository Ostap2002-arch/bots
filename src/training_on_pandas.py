import json
import sys
from datetime import datetime
from os.path import dirname, abspath
from math import sqrt
from typing import List, Tuple, Dict

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from src.models import BTCUSDT_table_ORM, Base
from src.queries.orm import select_data_by_date


def tunnel(prices: List[float], date: List[datetime]) -> Tuple[float, float, float, float]:
    """Функция создаёт тренд движения цены
    Эта функция принимает список данных о цене и времени. Массивы должны быть равного размера. На выход
    функция возвращает кортеж (A, B, B_UPP, B2_LOW). Где: A - коэффициент наклона тренда, B - смещение по y для
    основной линии тренда, B_UPP, B2_LOW - смещение для границ туннеля.

    Args:
        prices (List[float]): Список цен для построения тренда
        date: (List[datetime]): Список дат соответсвующее ценам

    Returns:
        Tuple[float, float, float]: Кортеж данных для построения тренда (A, B, B_UPP, B2_LOW)
    """
    date = [elem.timestamp() for elem in date]

    coefficients = np.polyfit(date, prices, 1)
    A, B = coefficients
    K = -1 / A

    deviations = list()

    for y1, x1 in zip(prices, date):
        C = y1 - K * x1
        x = (C - B) / (A - K)
        y = A * x + B
        l = sqrt((x - x1) ** 2 + (y - y1) ** 2)
        if y1 < y:
            l = -l
        deviations.append(l)

    deviations = np.array(deviations)
    mean = deviations.mean()
    variance = sqrt(np.var(deviations))

    COS = sqrt(1 / (1 + A ** 2))
    B_UPP = B + 2 * variance / COS
    B_LOW = B - 2 * variance / COS

    return A, B, B_UPP, B_LOW


def transfer_data_to_dict(data: List[Base]) -> dict:
    """Функция преобразование списка информации о барах в словарь.
    Эта функция на вход получает список экземпляров класса из бд и возвращает словарь, где: key - название атрибутов
    клаcса,
    value - список значений каждого экземпляра по данному атрибуту

    Args:
        data (List[Base]): Список экземпляров класса из бд

    Returns:
        dict: Словарь с преобразованной информацией. Пример {'id': [1, 2, ...], 'date': [datetime(2022-10-23),
        datetime(2023-04-15), ...], ...}
    """
    keys = [atr for atr in data[0].__dict__ if not atr.startswith('_')]
    result = {key: [] for key in keys}
    for elem in data:
        for key, value in result.items():
            value.append(elem.__dict__[key])
    return result


def print_data_dict(data: Dict[str, list]) -> None:
    """Функция печати данных в формате json
    Функция получает на вход словарь с данными и выводит на печать в удобном виде.
    При получении объектов не подлежащих сериализация, выводится их стороковое представление, кроме типа datetime. Для
    знакомства обработки объектов не подлежащих сериализация обратитесь к функции default_print.

    Args:
        data (Dict[str, list]): Словарь с данными

    Returns:
        None
    """
    print(json.dumps((data), indent=4, default=default_print))


def default_print(obj) -> str:
    """Функция представление объекта, при невозможности сериализация его в JSON.
    По-умолчанию все объекты
    будут представлены в строковом виде, кроме datetime.
    Тип данных datetime будет отображен в формате '%Y-%m-%d %H:%M:%S' """

    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return str(obj)


# -----------------------------------------------------------------------------------------------------------------------------------
data_base = select_data_by_date(BTCUSDT_table_ORM, datetime(2022, 11, 11), datetime(2022, 12, 7))
data_pres = select_data_by_date(BTCUSDT_table_ORM, datetime(2022, 11, 11), datetime(2022, 11, 21))

data_base = transfer_data_to_dict(data_base)
data_pres = transfer_data_to_dict(data_pres)

N = len(data_base['date'])
date_base = np.concatenate((data_base['date'], data_base['date'], data_base['date'], data_base['date']))
prices_base = np.concatenate((data_base['height_prise'], data_base['low_prise'], data_base['open_prise'], data_base['close_prise']))


date_pres = np.concatenate((data_pres['date'], data_pres['date'], data_pres['date'], data_pres['date']))
prices_pres = np.concatenate((data_pres['height_prise'], data_pres['low_prise'], data_pres['open_prise'], data_pres['close_prise']))

color = ['green'] * 2 * N + ['red'] * 2 * N

np.set_printoptions(precision=20, suppress=True)

A_pres, B_pres, B_UPP_pres, B_LOW_pres = tunnel(prices=list(prices_pres), date=list(date_pres))
A, B, B_UPP, B_LOW = tunnel(prices=list(prices_base), date=list(date_base))


date = [elem.timestamp() for elem in date_base]

x = date[:23]

poly_base = np.poly1d(np.array([A, B]))
y_base = poly_base(x)

poly_pres = np.poly1d(np.array([A_pres, B_pres]))
y_pres = poly_pres(x)


y_upp_base = A * np.array(x) + float(B_UPP)
y_low_base = A * np.array(x) + float(B_LOW)

y_upp_pres = A_pres * np.array(x) + float(B_UPP_pres)
y_low_pres = A_pres * np.array(x) + float(B_LOW_pres)

plt.scatter(date, prices_base, c=color, label='Диапазон цен')

plt.plot(x, y_base, label='Конечная линия тренда')
plt.plot(x, y_upp_base)
plt.plot(x, y_low_base)

plt.plot(x, y_pres, label='Прогнозная линия тренда', linestyle='--')
plt.plot(x, y_upp_pres, linestyle='--')
plt.plot(x, y_low_pres, linestyle='--')

plt.legend()
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Построение линии тренда с помощью аппроксимации')

plt.show()
