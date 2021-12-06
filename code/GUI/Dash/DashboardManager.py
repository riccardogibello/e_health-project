# This app is run at http://127.0.0.1:8050/.

import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd


def generate_table(dataframe, max_rows=10):
    return html.Table(
        style={'textAlign': 'center', 'marginLeft': 'auto', 'marginRight': 'auto'},
        children=[
            html.Thead(
                html.Tr([html.Th(col) for col in dataframe.columns])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
                ]) for i in range(min(len(dataframe), max_rows))
            ])
        ]
    )


app = dash.Dash(__name__)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

df = pd.read_csv('https://gist.githubusercontent.com/chriddyp/c78bf172206ce24f77d6363a2d754b59/raw'
                 '/c353e8ef842413cae56ae3920b8fd78468aa4cb2/usa-agricultural-exports-2011.csv')

app.layout = html.Div(children=[
    html.H1(
        children='Hello Dash',
        style={
            'backgroundColor': colors['background'],
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(style={
        'backgroundColor': colors['background'],
        'textAlign': 'center',
        'color': colors['text']
    },
        children='Dash: A web application framework for your data.'
    ),

    dcc.Graph(style={
        'backgroundColor': colors['background'],
        'color': colors['text']
    },
        id='example-graph-2',
        figure=fig
    ),

    html.H4(style={
        'textAlign': 'center',
        'color': colors['text']
    },
        children='US Agriculture Exports (2011)'
    ),

    generate_table(df)
])

if __name__ == '__main__':
    app.run_server(debug=True)
