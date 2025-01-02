import plotly.graph_objects as go

from obj import Stock
from strategy import MovingAverageCrossover

def plot_last_cumulative_roi_comparison(stock: Stock, buy_only: bool = False, buy_first: bool = False, show: bool = True, save_path: str = None) -> go.Figure:
    short_periods = [5, 10, 20, 60, 120, 240]
    long_periods = [5, 10, 20, 60, 120, 240]

    roi_values = []  # List to store ROI for each combination
    combinations = []  # List to store combinations of short and long periods

    # Loop over different short and long MA periods
    for s in short_periods:
        for l in long_periods:
            if s < l:  # Ensure that short MA is always less than long MA
                ma_info = MovingAverageCrossover(stock.data, s, l)
                if buy_only:
                    roi = stock.count_rois_and_cumulative_rois(ma_info['buy_dates'])
                else:
                    roi = stock.count_rois_and_cumulative_rois(ma_info['buy_dates'], ma_info['sell_dates'], buy_first=buy_first)
                roi_values.append(roi)
                combinations.append(f'{s}-{l}')

    # Create the plot
    trace = go.Scatter(
        x=combinations,
        y=roi_values,
        mode='markers',
        text=combinations,
        marker=dict(color=roi_values, colorscale='Viridis', size=12),
        name="ROI"
    )

    # Layout
    layout = go.Layout(
        title="ROI Comparison of Short and Long MA Combinations",
        xaxis=dict(title="Short MA - Long MA Combinations"),
        yaxis=dict(title="Last Cumulative ROI"),
        showlegend=False,
        hovermode='closest'
    )

    # Create the figure and display
    fig = go.Figure(data=[trace], layout=layout)

    if show:
        fig.show()
            
    if save_path is not None:
        fig.write_html(save_path)

    return fig