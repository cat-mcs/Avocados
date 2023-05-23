
import pandas as pd
import yfinance as yf
from dash import Dash, Input, Output, dcc, html
import plotly.graph_objects as go

def tickerData(tickerText):
    ticker = yf.Ticker(tickerText)
    tickerData = ticker.history(period="max")
    tickerData.reset_index(inplace=True)
    tickerData['Date'] = tickerData['Date'].dt.strftime('%Y-%m-%d')
    tickerData.drop(['Dividends', 'Stock Splits'], axis=1, inplace=True)
    tickerData.to_dict(orient='records')
    return tickerData

data = (
    tickerData("BTC-USD")
    .assign(Date=lambda data: pd.to_datetime(data["Date"], format="%Y-%m-%d"))
    .sort_values(by="Date")
)
print(data.head())

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
                        html.Div(children="Ticker", className="menu-title"),
                        dcc.Dropdown(
                            id="ticker-filter",
                            options=[
                                "BTC-USD","ETH-USD","ADA-USD","QNT-USD",
                                "ETH-BTC","ADA-ETH","QNT-BTC",
                            ],
                            value="BTC-USD",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
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
                
                    children=dcc.Graph(id="price-chart",
                              figure=go.Figure(data=go.Bar(x=data["Date"], y=data["Close"],marker_color="green"),
                                               layout=dict(template="plotly_dark"))),
                        className="card",),
                html.Div(

                    children=dcc.Graph(id="volume-chart",
                              figure=go.Figure(data=go.Bar(x=data["Date"], y=data["Volume"],marker_color="red"),
                                               layout=dict(template="plotly_dark"))),
                        className="card",),
                ],
                className="wrapper",)
    ]
)

@app.callback(
    Output("price-chart","figure"),
    Output("volume-chart","figure"),
    Input("ticker-filter", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_charts(ticker, start_date, end_date):
    
    data = tickerData(ticker)
    data = ( data[(data["Date"] >= start_date) & (data["Date"] <= end_date)] if start_date and end_date else data)

    pc = go.Figure(data=go.Line(x=data["Date"], y=data["Close"],marker_color="green"),layout=dict(template="plotly_dark"))
    vc = go.Figure(data=go.Line(x=data["Date"], y=data["Volume"],marker_color="red"),layout=dict(template="plotly_dark"))
    pc.update_xaxes(showgrid=False)
    pc.update_yaxes(showgrid=False)
    vc.update_xaxes(showgrid=False)
    vc.update_yaxes(showgrid=False)

    return pc, vc

if __name__ == "__main__":
    app.run_server(debug=True)