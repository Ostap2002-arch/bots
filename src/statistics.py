import math
import sys
from os.path import dirname, abspath
import numpy as np
from models import BTCUSDT_table_ORM
from queries.orm import select_data_orm
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, dirname(dirname(abspath(__file__))))

data = select_data_orm(BTCUSDT_table_ORM)


def find_statistic(data):
    np.set_printoptions(precision=5, suppress=True)
    open_prise = []
    close_prise = []
    height_prise = []
    low_prise = []

    for elem in data:
        open_prise.append(elem.open_prise)
        close_prise.append(elem.close_prise)
        height_prise.append(elem.height_prise)
        low_prise.append(elem.low_prise)

    # N - кол-во интервалов, на которые мы делим цены
    N = 50
    open_array = np.array(open_prise)
    close_array = np.array(close_prise)
    body = np.abs(open_array - close_array)
    body = body.round()

    M_X_q_left = None
    M_X_q_right = None

    while M_X_q_left is None or M_X_q_right is None or M_X_q_right < 0 or M_X_q_left < 0:
        if M_X_q_right is None:
            body = body
        else:
            if M_X_q_left < 0:
                body = body[body < M_X_q_right]
            else:
                body = body[body > M_X_q_left]
        intervals = np.linspace(0, body.max(), N)
        quantity = np.array([])
        probability = np.array([])
        result = (body < 0)
        result = np.count_nonzero(result)
        quantity = np.append(quantity, result)
        probability = np.append(probability, result / len(body))
        for left, right in zip(intervals, intervals[1:]):
            result = (body > left) & (body <= right)
            result = np.count_nonzero(result)
            quantity = np.append(quantity, result)
            probability = np.append(probability, result / len(body))

        M_X = np.sum(probability * intervals)
        M_X_2 = np.sum(probability * intervals * intervals)
        D_X = M_X_2 - M_X ** 2
        q = math.sqrt(D_X)
        M_X_q_left = M_X - q
        M_X_q_right = M_X + q
    return M_X_q_left, M_X_q_right


def find_static_percent(data):
    np.set_printoptions(precision=5, suppress=True)
    open_prise = []
    close_prise = []
    height_prise = []
    low_prise = []

    for elem in data:
        open_prise.append(elem.open_prise)
        close_prise.append(elem.close_prise)
        height_prise.append(elem.height_prise)
        low_prise.append(elem.low_prise)
    M_X_q_left = None
    M_X_q_right = None

    open_prise = np.array(open_prise)
    close_prise = np.array(close_prise)
    percent = (np.abs((open_prise - close_prise) / open_prise * 100)).round(3)

    while M_X_q_left is None or M_X_q_right is None or M_X_q_right < 0 or M_X_q_left < 0:
        if M_X_q_right is None:
            percent = percent
        else:
            if M_X_q_left < 0:
                percent = percent[percent < M_X_q_right]
            else:
                percent = percent[percent > M_X_q_left]
        q = np.std(percent)
        M_X = percent.mean()
        M_X_q_left = M_X - q
        M_X_q_right = M_X + q
    return M_X_q_left, M_X_q_right


def find_levels(data):
    np.set_printoptions(precision=5, suppress=True)
    open_prise = []
    close_prise = []
    height_prise = []
    low_prise = []
    date = []

    for elem in data:
        open_prise.append(elem.open_prise)
        close_prise.append(elem.close_prise)
        height_prise.append(elem.height_prise)
        low_prise.append(elem.low_prise)
        date.append(elem.date)

    open_prise = np.array(open_prise)
    close_prise = np.array(close_prise)
    height_prise = np.array(height_prise)
    low_prise = np.array(low_prise)

    upper = np.append(open_prise, height_prise)
    upper.sort()
    lower = np.append(close_prise, low_prise)
    lower.sort()

    copy_upper = upper.copy()
    copy_lower = lower.copy()

    def iter_values(copy_data, mode=None, border=None):
        copy_delta_data = np.diff(copy_data)
        left_upper = None
        right_upper = None

        while left_upper is None or right_upper is None or left_upper < 0 or right_upper < 0:
            if left_upper is not None:
                copy_delta_data = copy_delta_data[copy_delta_data < right_upper]
            M_upper = copy_delta_data.mean()
            q_upper = copy_delta_data.std()
            left_upper = M_upper - q_upper
            right_upper = M_upper + q_upper
            print(f'''
Мат ожидание = {M_upper} 
Дисперсия = {q_upper}
Левая граница = {left_upper}
Правая граница = {right_upper}
-------------------------------
''')

        prices = []
        repet = False
        result = []

        for i, elem in enumerate(copy_delta_data):
            if elem < left_upper or border is not None and elem < border:
                if not repet:
                    prices.append(copy_data[i])
                    prices.append(copy_data[i + 1])
                else:
                    prices.append(copy_data[i + 1])
            elif len(prices) != 0:
                prices = np.array(prices)
                result.append(prices.mean())
                prices = []
                repet = False
            else:
                if mode == 'united':
                    result.append(copy_data[i + 1])
        return result

    print('создаём все уровни')
    levels_upper = iter_values(copy_upper)
    levels_lower = iter_values(copy_lower)
    levels = levels_lower + levels_upper
    levels.sort()
    print(levels)
    print('объединяем')
    united_levels = iter_values(np.array(levels), mode='united')
    print(len(united_levels))

    plt.hist(united_levels, bins=1000, label='Уровни')
    plt.xlabel('Значения')
    plt.ylabel('Частота')
    plt.show()

    return united_levels


def find_level_with_min_delta(data):
    np.set_printoptions(precision=5, suppress=True)
    open_prise = []
    close_prise = []
    height_prise = []
    low_prise = []
    date = []

    for elem in data:
        open_prise.append(elem.open_prise)
        close_prise.append(elem.close_prise)
        height_prise.append(elem.height_prise)
        low_prise.append(elem.low_prise)
        date.append(elem.date)

    open_prise = np.array(open_prise)
    close_prise = np.array(close_prise)
    height_prise = np.array(height_prise)
    low_prise = np.array(low_prise)

    upper = np.append(open_prise, height_prise)
    upper.sort()
    lower = np.append(close_prise, low_prise)
    lower.sort()

    def find_min(array):
        delta = None
        pair = (None, None)
        for left, right in zip(array, array[1::]):
            if delta is None:
                delta = right - left
                continue
            new_delta = right - left
            if new_delta < delta:
                delta = new_delta
                pair = (left, right)
                continue
        return pair

    upper_level = np.array(find_min(upper)).mean()
    lower_level = np.array(find_min(lower)).mean()
    return float(upper_level), float(lower_level)
