import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Stock:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.rois = pd.DataFrame() # ['ROI', 'Cumulative_ROI']

    def count_rois_and_cumulative_rois(self, buy_dates: pd.Series, sell_dates: pd.Series = None, buy_first: bool = False) -> np.float64:
        """
        根據每筆交易的買入和賣出價格計算，報酬率與累計報酬率，並回傳最終的累計報酬率。

        :param buy_dates: 交易的買入日期。
        :param sell_dates: 交易的賣出日期。
        :return: 最終累計報酬率
        """
        
        if sell_dates is None:
            final_price = self.data['Close(NTD)'].iloc[-1]
            buy_prices = self.data['Close(NTD)'].loc[buy_dates]

            buy_prices_mean = buy_prices.mean()
            roi = (final_price - buy_prices_mean) / buy_prices_mean
            
            self.rois = pd.DataFrame([0.0, roi], columns=['ROI'], index=[buy_dates.min(), self.data.index.max()])
            self.rois['Cumulative_ROI'] = (1 + self.rois['ROI']).cumprod()

            return self.rois.iloc[-1]['Cumulative_ROI']

        if buy_first:
            return self._calculate_with_buy_first(buy_dates, sell_dates)
        else:
            return self._calculate_with_signal(buy_dates, sell_dates)

    def _calculate_with_buy_first(self, buy_dates: pd.Series, sell_dates: pd.Series) -> np.float64:      
        if sell_dates[0] < buy_dates[0]:
            sell_dates = sell_dates[1:]

        # 確保buy sell交替
        buy_sell_dates = []
        for i in range(len(buy_dates)):
            buy_sell_dates.append(buy_dates[i])
            if i < len(sell_dates):
                buy_sell_dates.append(sell_dates[i])
            else:
                break

        # 防止多一個buy
        if len(buy_sell_dates) % 2 != 0:
            buy_sell_dates.pop(-1)
        
        buy_prices = self.data['Close(NTD)'].loc[buy_sell_dates[::2]]
        sell_prices = self.data['Close(NTD)'].loc[buy_sell_dates[1::2]]

        rois = (sell_prices.values - buy_prices.values) / buy_prices.values
        self.rois = pd.DataFrame(rois, columns=['ROI'], index=sell_prices.index)

        self.rois['Cumulative_ROI'] = (1 + self.rois['ROI']).cumprod()

         # 合併buy_price和sell_price
        combined = pd.DataFrame({
            'Buy_Date': buy_prices.index,
            'Sell_Date': sell_prices.index,
            'Buy_Price': buy_prices.values,
            'Sell_Price': sell_prices.values,
            'ROI':self.rois['ROI'],
            'Cumulative_ROI':self.rois['Cumulative_ROI'] 
        })

        # 將結果寫入CSV檔案
        combined.to_csv('buy_sell_prices.csv', index=False, encoding='utf-8')
        
        return self.rois.iloc[-1]['Cumulative_ROI']
  
    def _calculate_with_signal(self, buy_dates: pd.Series, sell_dates: pd.Series) -> np.float64:
        trade_entries = self.data[['Close(NTD)']].copy()

        for date in buy_dates:
            trade_entries.loc[date, 'Signal'] = 1
        for date in sell_dates:
            trade_entries.loc[date, 'Signal'] = -1

        if trade_entries['Signal'].iloc[-1] == 1:
            trade_entries.loc[self.data.index[-1], 'Signal'] = -1
        elif trade_entries['Signal'].iloc[-1] == -1:
            trade_entries.loc[self.data.index[-1], 'Signal'] = 1
        
        trade_entries.dropna(inplace=True)
        
        trade_entries['ROI'] = 0.0
        for i in range(1, len(trade_entries)):
            entry_price = trade_entries.iloc[i - 1]['Close(NTD)']
            exit_price = trade_entries.iloc[i]['Close(NTD)']
            position = trade_entries.iloc[i - 1]['Signal']

            if position == 1:
                roi = (exit_price - entry_price) / entry_price
            elif position == -1:
                roi = (entry_price - exit_price) / entry_price
            else:
                roi = 0.0

            trade_entries.at[trade_entries.index[i], 'ROI'] = roi
        
        self.rois = trade_entries[['ROI']].copy()

        self.rois['Cumulative_ROI'] = (1 + self.rois['ROI']).cumprod()

        return self.rois.iloc[-1]['Cumulative_ROI']
    
    def draw_cumulative_rois_line_chart(self, show: bool = True, save_path: str = None) -> go.Figure:
        roi_line = go.Scatter(
            x=self.rois.index,
            y=self.rois['Cumulative_ROI'],
            mode='lines+markers',
            name='Cumulative ROI'
        )

        fig = go.Figure(roi_line)

        fig.update_layout(
            title="Cumulative ROI Over Trades",
            xaxis_title="Trades",
            yaxis_title="Cumulative ROI"
        )

        if show:
            fig.show()

        if save_path is not None:
            fig.write_html(save_path)

        return fig

    def draw_candlestick_trends(self, ma_info: dict = None, buy_dates: pd.Series = None, sell_dates: pd.Series = None, show: bool = True, save_path: str = None) -> go.Figure:
        candlestick = go.Candlestick(
            x=self.data.index,
            open=self.data['Open(NTD)'],
            high=self.data['High(NTD)'],
            low=self.data['Low(NTD)'],
            close=self.data['Close(NTD)'],
            increasing_line_color='red',
            decreasing_line_color='green',
            name='Candlestick'
        )

        volume_color = [
            'red' if self.data['Close(NTD)'].iloc[i] >= self.data['Open(NTD)'].iloc[i] else 'green' for i in range(len(self.data))
        ]

        bar = go.Bar(
            x=self.data.index,
            y=self.data['Volume(1000S)'],
            marker_color=volume_color,
            name='Trading Volume'
        )

        if ma_info is not None:
            short_ma_line = go.Scatter(
                x=self.data.index,
                y=ma_info['short_ma'],
                name=ma_info['short_ma_name'],
                line=dict(
                    color='blue',
                    dash='dash'
                )
            )

            long_ma_line = go.Scatter(
                x=self.data.index,
                y=ma_info['long_ma'],
                name=ma_info['long_ma_name'],
                line=dict(
                    color='purple',
                    dash='dot'
                )
            )

        if buy_dates is not None:
            buy_scatter = go.Scatter(
                x=buy_dates,
                y=self.data['Close(NTD)'][buy_dates],
                mode='markers',
                marker=dict(color='red', size=12, symbol='triangle-up'),
                name='Buy Signal'
            )   
            
        if sell_dates is not None:
            sell_scatter = go.Scatter(
                x=sell_dates,
                y=self.data['Close(NTD)'][sell_dates],
                mode='markers',
                marker=dict(color='green', size=12, symbol='triangle-down'),
                name='Sell Signal'
            )

        fig = make_subplots(rows=2, cols=1, row_heights=[0.8, 0.2], shared_xaxes=True)

        fig.add_trace(candlestick, row=1, col=1)
        fig.add_trace(bar, row=2, col=1)

        if ma_info is not None:
            fig.add_trace(short_ma_line, row=1, col=1)
            fig.add_trace(long_ma_line, row=1, col=1)

        fig.update_layout(
            xaxis_rangeslider_visible=False,
            hovermode='x unified'
        )

        if buy_dates is not None:
            fig.add_trace(buy_scatter, row=1, col=1)

            buy_signals = self.data.loc[buy_dates].copy()
            for date, price in zip(buy_signals.index, buy_signals['Close(NTD)']):
                fig.add_shape(
                    type="line",
                    x0=date,
                    y0=min(self.data['Close(NTD)']),
                    x1=date,
                    y1=price,
                    line=dict(color="red", width=1.5, dash="dot")
                )

        if sell_dates is not None:
            fig.add_trace(sell_scatter, row=1, col=1)

            sell_signals = self.data.loc[sell_dates].copy()
            for date, price in zip(sell_signals.index, sell_signals['Close(NTD)']):
                fig.add_shape(
                    type="line",
                    x0=date,
                    y0=min(self.data['Close(NTD)']),
                    x1=date,
                    y1=price,
                    line=dict(color="green", width=1.5, dash="dot")
                )
        
        if show:
            fig.show()

        if save_path is not None:
            fig.write_html(save_path)

        return fig

    def draw_rois_bar_chart(self, strategy_names: list[str], last_cumulative_rois: list[np.float64], colors: list[str] = None, show: bool = True, save_path: str = None) -> go.Figure:
        fig = go.Figure(go.Bar(x=strategy_names, y=last_cumulative_rois, text=last_cumulative_rois, textposition='auto', marker_color=colors))
        fig.update_traces(texttemplate='%{text:.4f}', textposition='outside')

        if show:
            fig.show()
        
        if save_path is not None:
            fig.write_html(save_path)
        
        return fig

