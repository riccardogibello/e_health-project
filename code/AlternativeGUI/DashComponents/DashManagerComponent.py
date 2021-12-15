import play_scraper
from dash import dcc, dash, callback_context
from dash import html
import dash_bootstrap_components as dbc
from AlternativeGUI.DashComponents.DashPagesCreators.IndexPageCreator import get_index_page
from AlternativeGUI.DashComponents.DashPagesCreators.OverviewDashCreator import get_overview_dash_page
from AlternativeGUI.DashComponents.DashPagesCreators.SpecificDashCreator import get_specific_dash_page, \
    compute_options_for_papers, compute_list_of_dictionary_label_value, compute_options_for_applications, \
    compute_options_for_authors
from DataManagers.DatabaseManager import do_query

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

reset_paper_button_click = 0


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


@app.callback([dash.Output(component_id='app_dropdown', component_property='options')],
              [dash.Input(component_id='paper-dropdown', component_property='value')])
def get_apps_related_to_papers(paper_id):
    query = 'SELECT sa.app_id, sa.app_name ' \
            'FROM selected_app AS sa JOIN app_paper AS ap ' \
            'ON sa.app_id = ap.app_id ' \
            'WHERE ap.paper_id = %s'
    results = do_query((paper_id,), query)

    if not results:
        apps = compute_options_for_applications()

        return [dcc.Dropdown(
            options=apps,
            placeholder="Write here the name of a paper"
        )]

    list_ = compute_list_of_dictionary_label_value(results)
    return dcc.Dropdown(
        options=list_,
        placeholder="Write here the name of an app"
    )


@app.callback([dash.Output(component_id='app_data_table', component_property='children')],
              [dash.Input(component_id='app_dropdown', component_property='value'),
               dash.Input(component_id='reset-button', component_property='n_clicks')])
def get_app_data(app_id, n_clicks):
    query = 'SELECT app_id, app_name, category_id, score, rating, installs, ' \
            'last_update, content_rating, teacher_approved FROM selected_app WHERE app_id = %s LIMIT 1'
    results = do_query((app_id,), query)
    data = ['Application Identifier : ', 'Application Name : ',
            'Category : ', 'Score : ', 'Rating : ', 'Installs : ', 'Last Update : ', 'Content Rating : ',
            'Teacher Approved : ']

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'reset-button' in changed_id:
        return [html.Table()]

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
              [dash.Input(component_id='app_dropdown', component_property='value'),
               dash.Input(component_id='reset-button', component_property='n_clicks')])
def get_image_data(app_id, n_clicks):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'reset-button' in changed_id:
        return [html.Img()]

    if app_id:
        result = play_scraper.details(app_id)
        return [html.Img(src=result['icon'], width="150", height="150")]
    else:
        return [html.Img()]


@app.callback([dash.Output(component_id='paper_dropdown', component_property='placeholder'),
               dash.Output(component_id='paper_dropdown', component_property='options')],
              [dash.Input(component_id='app_dropdown', component_property='value'),
               dash.Input(component_id='reset-papers-button', component_property='n_clicks'),
               dash.Input(component_id='reset-button', component_property='n_clicks')])
def get_papers_related_to_app(app_id, n_clicks, n_clicks_2):
    query = 'SELECT p.paper_id, p.paper_title ' \
            'FROM paper AS p JOIN app_paper AS ap ' \
            'ON p.paper_id = ap.paper_id ' \
            'WHERE ap.app_id = %s'
    results = do_query((app_id,), query)

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'reset-papers-button' in changed_id or 'reset-button' in changed_id or app_id is None:
        papers = compute_options_for_papers()
        return ["Write here the name of a paper", papers]
    if not results:
        return ['Write here the name of a paper', []]

    papers = compute_list_of_dictionary_label_value(results)
    return ['Write here the name of a paper', papers]


@app.callback([dash.Output(component_id='label_author', component_property='children')],
              [dash.Input(component_id='author_dropdown', component_property='value'),
               dash.Input(component_id='reset-authors-button', component_property='n_clicks'),
               dash.Input(component_id='reset-button', component_property='n_clicks')])
def get_author_publications(author_id, n_clicks, n_clicks_2):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'reset-authors-button' in changed_id or 'reset-button' in changed_id:
        return [html.Label()]

    if author_id is not None:
        query = 'SELECT name, surname FROM author WHERE author_id = %s LIMIT 1'
        results = do_query((author_id,), query)
        name = results[0][0]
        surname = results[0][1]

        query = 'SELECT papers FROM author WHERE author_id = %s LIMIT 1'
        results = do_query((author_id,), query)

        if not results:
            publications = 0
        else:
            publications = results[0][0]
        return [html.Label(name + ' ' + surname + ' has ' + str(publications) + ' publications on PubMed.')]
    else:
        return [html.Label()]


@app.callback([dash.Output(component_id='author_dropdown', component_property='options')],
              [dash.Input(component_id='paper_dropdown', component_property='value'),
               dash.Input(component_id='reset-authors-button', component_property='n_clicks'),
               dash.Input(component_id='reset-papers-button', component_property='n_clicks'),
               dash.Input(component_id='reset-button', component_property='n_clicks')])
def get_authors_related_to_paper(paper_id, n_clicks_1, n_clicks_2, n_clicks_3):
    query = 'SELECT a.author_id, a.name, a.surname ' \
            'FROM author AS a, author_paper AS ap WHERE a.author_id = ap.author_id AND ap.paper_id = %s'
    results = do_query((paper_id,), query)

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'reset-authors-button' in changed_id or 'reset-papers-button' in changed_id \
            or 'reset-button' in changed_id or paper_id == '':
        authors = compute_options_for_authors()
        return [authors]
    if not results:
        return [[]]

    dictionary_label_value__list = []
    for result in results:
        dictionary = {}
        author_id = result[0]
        surname_name = result[2] + ', ' + result[1]
        name_len = len(surname_name)
        if name_len - 1 > 45:
            surname_name = surname_name[:45] + '...'
        dictionary.__setitem__('label', surname_name)
        dictionary.__setitem__('value', author_id)
        dictionary_label_value__list.append(dictionary)

    return [dictionary_label_value__list]


@app.callback([dash.Output(component_id='paper_data_table', component_property='children')],
              [dash.Input(component_id='paper_dropdown', component_property='value'),
               dash.Input(component_id='reset-papers-button', component_property='n_clicks'),
               dash.Input(component_id='reset-button', component_property='n_clicks')])
def get_paper_data(paper_id, n_clicks, c_clicks_2):
    query = 'SELECT paper_title, abstract, type FROM paper WHERE paper_id = %s LIMIT 1'
    result = do_query((paper_id,), query)
    labels = ['Paper Title : ', 'Paper Abstract : ', 'Type of Paper : ']

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'reset-papers-button' in changed_id or 'reset-button' in changed_id or paper_id is None:
        return [html.Table()]

    if result:
        data = result[0]

        table_children_rows = []
        i = 0
        for label in labels:
            datum = data[i]
            row = html.Tr(
                children=[
                    html.Td(label, style={'font-weight': 'bold'}),
                    html.Td(datum, style={'width': '80%'})
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


if __name__ == '__main__':
    run_dash()
