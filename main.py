import pandas as pd

from obj import Stock
from utils import plot_last_cumulative_roi_comparison
from strategy import DollarCostAveraging, MovingAverageCrossover

file_path = './data/English_Version_9921_20070102_20241211.xlsx'

data = pd.read_excel(file_path)
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

stock_9921 = Stock(data)

rois_dict = {}

# --- DollarCostAveraging ---

dca_buy_dates = DollarCostAveraging(data)
dca_cumulative_roi = stock_9921.count_rois_and_cumulative_rois(dca_buy_dates)
rois_dict['DCA'] = dca_cumulative_roi
stock_9921.draw_cumulative_rois_line_chart()
stock_9921.draw_candlestick_trends(buy_dates=dca_buy_dates)


# --- MovingAverageCrossover ---

plot_last_cumulative_roi_comparison(stock_9921)
plot_last_cumulative_roi_comparison(stock_9921, buy_only=True)
plot_last_cumulative_roi_comparison(stock_9921, buy_first=True)

ma_info = MovingAverageCrossover(data, 20, 120)
mac_cumulative_roi = stock_9921.count_rois_and_cumulative_rois(ma_info['buy_dates'], ma_info['sell_dates'])
rois_dict['MAC'] = mac_cumulative_roi
stock_9921.draw_cumulative_rois_line_chart()
stock_9921.draw_candlestick_trends(ma_info, ma_info['buy_dates'], ma_info['sell_dates'])

ma_info = MovingAverageCrossover(data, 20, 240)
mac_cumulative_roi = stock_9921.count_rois_and_cumulative_rois(ma_info['buy_dates'])
rois_dict['MAC(buy only)'] = mac_cumulative_roi
stock_9921.draw_cumulative_rois_line_chart()
stock_9921.draw_candlestick_trends(ma_info, ma_info['buy_dates'], ma_info['sell_dates'])

ma_info = MovingAverageCrossover(data, 10, 20)
mac_cumulative_roi = stock_9921.count_rois_and_cumulative_rois(ma_info['buy_dates'], ma_info['sell_dates'], buy_first=True)
rois_dict['MAC(buy_first)'] = mac_cumulative_roi
stock_9921.draw_cumulative_rois_line_chart()
stock_9921.draw_candlestick_trends(ma_info, ma_info['buy_dates'], ma_info['sell_dates'])


# --- compare the last cumulative roi from diffrent strategies ---

stock_9921.draw_rois_bar_chart(list(rois_dict.keys()), list(rois_dict.values()))