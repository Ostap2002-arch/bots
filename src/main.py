import sys
from os.path import dirname, abspath
import pandas as pd
import mplfinance as mpf

from src.avg import avg, avg_body
from src.utils import color_anomalies, avg_lines

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from src.models import BTCUSDT_table_ORM
from src.queries.orm import select_data_orm

data = select_data_orm(BTCUSDT_table_ORM)

date = []
open_prise = []
close_prise = []
height_prise = []
low_prise = []

for elem in data:
    date.append(elem.date)
    open_prise.append(elem.open_prise)
    close_prise.append(elem.close_prise)
    height_prise.append(elem.height_prise)
    low_prise.append(elem.low_prise)

df = pd.DataFrame({
    "Open": open_prise,
    "High": height_prise,
    "Low": low_prise,
    "Close": close_prise,
},
    index=date
)
df.index.name = "Date"


mpf.plot(df, type='candle', alines=avg_lines(prices=close_prise, date=date, N={30: 'r', 20: 'b'}))


color = color_anomalies(open_prise=height_prise, close_prise=low_prise, N=10)
mpf.plot(df, type='candle', marketcolor_overrides=color)
