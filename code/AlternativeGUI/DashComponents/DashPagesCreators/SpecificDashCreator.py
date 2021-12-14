from dash import html, dcc
from DataManagers.DatabaseManager import do_query


def compute_list_of_dictionary_label_value(results):
    dictionary_label_value__list = []
    for result in results:
        dictionary = {}
        id = result[0]
        name_displayed = result[1]
        name_len = len(name_displayed)
        if name_len - 1 > 45:
            name_displayed = name_displayed[:45] + '...'
        dictionary.__setitem__('label', name_displayed)
        dictionary.__setitem__('value', id)
        dictionary_label_value__list.append(dictionary)

    return dictionary_label_value__list


def compute_options_for_applications():
    query = 'SELECT app_id, app_name FROM selected_app'
    results = do_query((), query)
    return compute_list_of_dictionary_label_value(results)


def compute_options_for_papers():
    query = 'SELECT paper_id, paper_title FROM paper'
    results = do_query((), query)

    return compute_list_of_dictionary_label_value(results)


def get_specific_dash_page():
    colors = {
        'background': '#34568b',
        'text': '#000000'
    }

    applications = compute_options_for_applications()  # this must be a list of dictionaries,
    # in which every dictionary is composed by { 'label' : 'app_name', 'value' : 'app_id' }

    papers = compute_options_for_papers()

    layout = html.Div(
        children=[
            html.Table(
                children=[
                    html.Tr(html.Td(dcc.Link('Go back', href='/')))],
                style={'border': 'solid 2px',
                       'border-radius': '10px',
                       'margin-right': '10px',
                       'margin-left': 'auto',
                       'display': 'inline-block',
                       'background': '#ADD8E6'}),
            html.Div(
                children=[
                    html.Table(
                        style={'border': '2px solid black',
                               'border-collapse': 'separate',
                               'border-radius': '15px',
                               'border-spacing': '20px',
                               'margin-top': '50px',
                               'margin-bottom': '50px',
                               'background': '#ADD8E6',
                               'min-width': '500px'},
                        children=[
                            html.Header(html.Th(colSpan=2, children=['Search for a serious game application!'],
                                                style={
                                                    'textAlign': 'center',
                                                    'color': colors['text']
                                                })),
                            html.Tr(
                                children=[
                                    html.Td(
                                        children=[
                                            dcc.Dropdown(
                                                id='app_dropdown',
                                                options=applications,
                                                placeholder="Write here the name of an application")
                                        ]
                                    )
                                ]
                            ),
                            html.Tr(
                                children=[
                                    html.Td(
                                        html.Div(
                                            id='app_icon_image',
                                            children=html.Img(src='')
                                        )
                                    )
                                ]
                            )
                        ]
                    ),
                    # the following will contain the data about the application chosen
                    html.Div(id='app_data_table',
                             children=[
                                 html.Table()
                             ])
                ], style={'text-align': 'center', 'display': 'flex', 'justify-content': 'center'})
            ,
            html.Table(
                style={'border': '2px solid black',
                       'border-collapse': 'separate',
                       'border-radius': '15px',
                       'border-spacing': '20px',
                       'margin-left': 'auto',
                       'margin-right': 'auto',
                       'margin-top': '50px',
                       'margin-bottom': '50px',
                       'background': '#ADD8E6',
                       'display': 'table',
                       'min-width': '500px'},
                children=[
                    html.Header(html.Th(
                        colSpan=2,
                        children=['Search for a paper by keyword!']),
                        style={
                            'textAlign': 'center',
                            'color': colors['text']
                        }
                    ),
                    html.Tr(
                        children=[
                            html.Td(
                                children=[
                                    dcc.Dropdown(
                                        id='paper_dropdown',
                                        options=papers,
                                        placeholder="Write here the name of a paper"
                                    ),
                                ]
                            )
                        ]
                    )
                ]
            )
        ], style={'background': '#4682B4',
                  'margin-left': '20px',
                  'margin-right': '20px',
                  'margin-top': '17px',
                  'margin-bottom': '10px',
                  'border-radius': '20px',
                  'padding': '20px'}
    )

    return layout
