from models import BTCUSDT_table_ORM
from queries.orm import select_data_orm, update_table

N = 2
list_N = list()
Total_extreme = 1
data = select_data_orm(BTCUSDT_table_ORM)
length_result = len(data)

while Total_extreme:
    Total_extreme = 0
    for i in range(length_result):
        absolute_elem = data[i]
        if i - N >= 0:
            border_left = i - N
        elif i - N < 0:
            border_left = 0
        if i + N <= length_result - 1:
            border_right = i + N
        elif i + N > length_result - 1:
            border_right = length_result - 1
        list_neighbors = data[border_left:border_right + 1]
        list_neighbors.remove(absolute_elem)
        if absolute_elem.low_prise < min(list_neighbors, key=lambda x: x.low_prise).low_prise:
            Total_extreme += 1
        if absolute_elem.height_prise > max(list_neighbors, key=lambda x: x.height_prise).height_prise:
            Total_extreme += 1
    # print(f"Total_extreme = {Total_extreme}, N = {N}, % = {round(Total_extreme/length_result * 100, 2)}")
    list_N.append((N, round(Total_extreme / length_result * 100, 2)))
    if round(Total_extreme / length_result * 100, 2) < 1:
        break
    N += 1
print(list_N)

# Делаем выборку по процентам
N_30 = min(list_N, key=lambda x: abs(x[1] - 30))
N_20 = min(list_N, key=lambda x: abs(x[1] - 20))
N_10 = min(list_N, key=lambda x: abs(x[1] - 10))
N_5 = min(list_N, key=lambda x: abs(x[1] - 5))
N_1 = min(list_N, key=lambda x: abs(x[1] - 1))

list_N = [N_30[0], N_20[0], N_10[0], N_5[0], N_1[0]]
dict_N = {k: v for k, v in zip(list_N, ['30', '20', '10', '5', '1'])}

for N in list_N:
    for i in range(length_result):
        absolute_elem = data[i]
        if i - N >= 0:
            border_left = i - N
        elif i - N < 0:
            border_left = 0
        if i + N <= length_result - 1:
            border_right = i + N
        elif i + N > length_result - 1:
            border_right = length_result - 1
        list_neighbors = data[border_left:border_right + 1]
        list_neighbors.remove(absolute_elem)
        if absolute_elem.low_prise < min(list_neighbors, key=lambda x: x.low_prise).low_prise:
            update_table(absolute_elem, **{f'relative_low_{dict_N[N]}': True})
        elif absolute_elem.height_prise > max(list_neighbors, key=lambda x: x.height_prise).height_prise:
            update_table(absolute_elem, **{f'relative_height_{dict_N[N]}': True})
        else:
            continue
