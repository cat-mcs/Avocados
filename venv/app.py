
import pandas as pd
import yfinance as yf
from dash import Dash, Input, Output, dcc, html

btc = yf.Ticker("BTC-USD")
btc_data = btc.history(period="max")
btc_data.reset_index(inplace=True)
btc_data['Date'] = btc_data['Date'].dt.strftime('%Y-%m-%d')
btc_data.drop(['Dividends', 'Stock Splits'], axis=1, inplace=True)
btc_data.to_dict(orient='records')

data = (
    btc_data
    .assign(Date=lambda data: pd.to_datetime(data["Date"], format="%Y-%m-%d"))
    .sort_values(by="Date")
)

external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Crypto Data"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="📡", className="header-emoji"),
                html.H1(
                    children="YFINANCE API: CRYPTO DATA", className="header-title"
                ),
                html.P(
                    children=(
                        "visualising cryptocurrency data provided by yahoo."
                    ),
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range", className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data["Date"].min().date(),
                            max_date_allowed=data["Date"].max().date(),
                            start_date=data["Date"].min().date(),
                            end_date=data["Date"].max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="price-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="volume-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)

@app.callback(
    Output("price-chart", "figure"),
    Output("volume-chart", "figure"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_charts(start_date, end_date):
    filtered_data = data.query(
        "Date >= @start_date and Date <= @end_date"
    )
    price_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Close"],
                "type": "lines",
                "hovertemplate": "$%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "BTC-USD Closing Price",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }

    volume_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Volume"],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {"text": "BTC-USD Daily Volume", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    return price_chart_figure, volume_chart_figure

if __name__ == "__main__":
    app.run_server(debug=True)