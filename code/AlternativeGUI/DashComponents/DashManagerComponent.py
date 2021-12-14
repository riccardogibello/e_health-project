import play_scraper
from dash import dcc, dash
from dash import html
import dash_bootstrap_components as dbc
from AlternativeGUI.DashComponents.DashPagesCreators.IndexPageCreator import get_index_page
from AlternativeGUI.DashComponents.DashPagesCreators.OverviewDashCreator import get_overview_dash_page
from AlternativeGUI.DashComponents.DashPagesCreators.SpecificDashCreator import get_specific_dash_page
from DataManagers.DatabaseManager import do_query

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)


def run_dash():
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content', style={'backgroundColor': '#34568b', 'width': '100%',
                                           'height': '100%', 'position': 'fixed', "overflowY": "scroll"})
    ])
    # without 'position': 'fixed', "overflowY": "scroll" the page won't scroll!

    app.run_server(debug=False)
    # TODO : set debug to False to run in finaly version


# Update the index
@app.callback(dash.Output('page-content', 'children'),
              [dash.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/overview_dash':
        return get_overview_dash_page()
    elif pathname == '/specific_dash':
        return get_specific_dash_page()
    else:
        print('hi')
        return get_index_page()


@app.callback([dash.Output(component_id='app_data_table', component_property='children')],
              [dash.Input(component_id='app_dropdown', component_property='value')])
def get_app_data(app_id):
    query = 'SELECT app_id, app_name, category_id, score, rating, installs, ' \
            'last_update, content_rating, teacher_approved FROM selected_app WHERE app_id = %s LIMIT 1'
    results = do_query((app_id,), query)
    data = ['Application Identifier : ', 'Application Name : ',
            'Category : ', 'Score : ', 'Rating : ', 'Installs : ', 'Last Update : ', 'Content Rating : ',
            'Teacher Approved : ']

    if results:
        table_children_rows = []
        i = 0
        for datum in data:
            if not datum == 'Teacher Approved : ':
                string_to_set = results[0][i]
            else:
                if int(results[0][i]):
                    string_to_set = 'Yes'
                else:
                    string_to_set = 'No'
            row = html.Tr(
                children=[
                    html.Td(datum, style={'font-weight': 'bold'}),
                    html.Td(string_to_set)
                ]
            )
            table_children_rows.append(row)
            i = i + 1

        data_table = html.Table(
            style={'border': '2px solid black',
                   'border-collapse': 'separate',
                   'border-radius': '15px',
                   'border-spacing': '20px',
                   'margin-left': '70px',
                   'margin-top': '50px',
                   'margin-bottom': '50px',
                   'background': '#ADD8E6'},
            children=table_children_rows
        )

        return [data_table]
    else:
        return [html.Table()]


@app.callback([dash.Output(component_id='app_icon_image', component_property='children')],
              [dash.Input(component_id='app_dropdown', component_property='value')])
def get_image_data(app_id):
    if app_id:
        result = play_scraper.details(app_id)
        return [html.Img(src=result['icon'], width="150", height="150")]
    else:
        return [html.Img()]


if __name__ == '__main__':
    run_dash()
