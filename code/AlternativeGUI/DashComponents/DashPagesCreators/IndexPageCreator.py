from dash import html, dcc


def get_index_page():
    layout = html.Div(
        children=[
            html.Div([
                html.Table(
                    children=[
                        html.Tr(
                            children=[
                                html.Td(children=[dcc.Link('Go to the Overview Dash', href='/overview_dash',
                                                           style={'font-size': '25px'})],
                                        style={'padding': '40px'}),
                                html.Td(children=[dcc.Link('Go to the Specific Dash', href='/specific_dash',
                                                           style={'font-size': '25px'})],
                                        style={'padding': '40px'})
                            ])
                    ],
                    style={'border': '2px solid black',
                           'border-collapse': 'separate',
                           'border-radius': '30px',
                           'borderSpacing': '10px',
                           'margin-left': 'auto',
                           'margin-right': 'auto',
                           'background': '#ADD8E6'})
            ],
                style={'display': 'table-cell', 'vertical-align': 'middle'})],
        style={'display': 'table',
               'position': 'absolute',
               'top': '0',
               'left': '0',
               'height': '100%',
               'width': '100%'})

    return layout
