import datetime

import play_scraper
from dash import dcc, dash, callback_context
from dash import html
import dash_bootstrap_components as dbc
from GUI.DashComponents.DashPagesCreators.IndexPageCreator import get_index_page
from GUI.DashComponents.DashPagesCreators.OverviewDashCreator import get_overview_dash_page, \
    compute_evidence_graph
from GUI.DashComponents.DashPagesCreators.SpecificDashCreator import get_specific_dash_page, \
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


# Update the index
@app.callback(dash.Output('page-content', 'children'),
              [dash.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/overview_dash':
        return get_overview_dash_page()
    elif pathname == '/specific_dash':
        return get_specific_dash_page()
    else:
        return get_index_page()


@app.callback([dash.Output(component_id='app_dropdown', component_property='options')],
              [dash.Input(component_id='filter-evidence-apps-button-2', component_property='n_clicks')])
def get_apps_with_evidence(n_clicks):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'filter-evidence-apps-button-2' in changed_id:
        query = 'SELECT app_id, app_name FROM selected_app WHERE app_id IN (SELECT app_id FROM app_paper)'
        results = do_query((), query)
        return [compute_list_of_dictionary_label_value(results)]
    else:
        return [compute_options_for_applications()]


@app.callback([dash.Output(component_id='app_data_table', component_property='children')],
              [dash.Input(component_id='app_dropdown', component_property='value'),
               dash.Input(component_id='reset-button', component_property='n_clicks')])
def get_app_data(app_id, n_clicks):
    query = 'SELECT app_id, app_name, category_id, d.name, score, rating, installs, ' \
            'last_update, content_rating, teacher_approved FROM selected_app AS sa, developer AS d WHERE ' \
            'sa.developer_id = d.id AND app_id = %s LIMIT 1'
    results = do_query((app_id,), query)
    data = ['Application Identifier : ', 'Application Name : ',
            'Category : ', 'Developer : ', 'Score : ', 'Number of reviews : ', 'Installs : ', 'Last Update : ',
            'Content Rating : ', 'Teacher Approved : ']

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'reset-button' in changed_id:
        return [html.Table()]

    if results:
        table_children_rows = []
        i = 0
        for datum in data:
            if datum == 'Teacher Approved : ':
                if int(results[0][i]):
                    string_to_set = 'Yes'
                else:
                    string_to_set = 'No'
            elif datum == 'Last Update : ':
                string_to_set = str(datetime.datetime.fromtimestamp(int(results[0][i])))
                string_to_set = string_to_set.split(' ')[0]
            elif datum == 'Score : ':
                string_to_set = str(float(results[0][i]).__format__('.2f'))
            else:
                string_to_set = results[0][i]
            row = html.Tr(
                children=[
                    html.Td(datum, style={'font-weight': 'bold', 'word-wrap': 'break-word'}),
                    html.Td(string_to_set, style={'word-wrap': 'break-word'})
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
                   'background': '#ADD8E6',
                   'width': '500px',
                   'table-layout': 'fixed'},
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


@app.callback([dash.Output(component_id='paper_dropdown', component_property='options')],
              [dash.Input(component_id='app_dropdown', component_property='value'),
               dash.Input(component_id='reset-papers-button', component_property='n_clicks'),
               dash.Input(component_id='reset-button', component_property='n_clicks'),
               dash.Input(component_id='study_type_dropdown', component_property='value')])
def get_papers_related_to_app(app_id, n_clicks, n_clicks_2, study_types):
    results = []
    if study_types and app_id:
        query = 'SELECT p.paper_id, p.paper_title ' \
                'FROM paper AS p JOIN app_paper AS ap ' \
                'ON p.paper_id = ap.paper_id ' \
                'WHERE ap.app_id = %s'
        par_list = [app_id]
        i = 0
        for study_type in study_types:
            if i == 0:
                query = query + ' AND (p.type = %s'
            else:
                query = query + ' OR p.type = %s'
            par_list.append(study_type)
            i = i + 1
        query = query + ')'
        results = do_query(par_list, query)
    elif study_types:
        query = 'SELECT p.paper_id, p.paper_title ' \
                'FROM paper AS p'
        par_list = []
        i = 0
        for study_type in study_types:
            if i == 0:
                query = query + ' WHERE p.type = %s'
            else:
                query = query + ' OR p.type = %s'
            par_list.append(study_type)
            i = i + 1
        results = do_query(par_list, query)
    elif app_id:
        query = 'SELECT p.paper_id, p.paper_title ' \
                'FROM paper AS p JOIN app_paper AS ap ' \
                'ON p.paper_id = ap.paper_id ' \
                'WHERE ap.app_id = %s'
        results = do_query((app_id,), query)

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'reset-papers-button' in changed_id or 'reset-button' in changed_id or (
            app_id is None and study_types is None) or (
            study_types is not None and len(study_types) == 0 and app_id is None):
        papers = compute_options_for_papers()
        return [papers]
    if not results:
        return [[]]

    papers = compute_list_of_dictionary_label_value(results)
    return [papers]


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
    query = 'SELECT paper_title, abstract, type, journal, nature_type FROM paper WHERE paper_id = %s LIMIT 1'
    result = do_query((paper_id,), query)
    labels = ['Paper Title : ', 'Paper Abstract : ', 'Type of Study : ', 'Journal : ', 'Type : ']

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'reset-papers-button' in changed_id or 'reset-button' in changed_id or paper_id is None:
        return [html.Table()]

    if result:
        data = result[0]

        table_children_rows = []
        i = 0
        for label in labels:
            datum = data[i]
            if label == 'Paper Abstract : ':
                row = html.Tr(
                    children=[
                        html.Td(label, style={'font-weight': 'bold', 'word-wrap': 'break-word'}),
                        html.Table(
                            style={'width': '100%'},
                            children=[
                                html.Tr(
                                    children=[
                                        html.Td(html.Button('Show abstract', id='show-abstract-button')),
                                        html.Td(html.Button('Hide abstract', id='hide-abstract-button'))
                                    ]
                                ),
                                html.Tr(id='abstract_line',
                                        children=html.Td(
                                            html.Div(
                                                html.Label(datum)
                                            ),
                                            colSpan=2
                                        ),
                                        style={'word-wrap': 'break-word'})
                            ]
                        )
                    ]
                )
            else:
                row = html.Tr(
                    children=[
                        html.Td(label, style={'font-weight': 'bold', 'word-wrap': 'break-word'}),
                        html.Td(datum, style={'word-wrap': 'break-word'})
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
                   'background': '#ADD8E6',
                   'width': '700px',
                   'table-layout': 'fixed'},
            children=table_children_rows
        )

        return [data_table]
    else:
        return [html.Table()]


@app.callback([dash.Output(component_id='abstract_line', component_property='children')],
              [dash.Input(component_id='paper_dropdown', component_property='value'),
               dash.Input(component_id='show-abstract-button', component_property='n_clicks'),
               dash.Input(component_id='hide-abstract-button', component_property='n_clicks')])
def show_hide_paper_abstract(paper_id, n_clicks1, n_clicks2):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'hide-abstract-button' in changed_id:
        return [html.Label()]
    elif 'show-abstract-button' in changed_id and paper_id:
        query = 'SELECT abstract FROM paper WHERE paper_id = %s'
        abstract = do_query((paper_id,), query)[0][0]
        return [html.Td(
            html.Div(
                html.Label(abstract)
            ),
            colSpan=2
        )]


@app.callback([dash.Output(component_id='app_evidence_dropdown', component_property='options')],
              [dash.Input(component_id='reset-evidence-button', component_property='n_clicks'),
               dash.Input(component_id='filter-evidence-apps-button-1', component_property='n_clicks')])
def reset_apps_options(n_clicks1, n_clicks2):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'reset-evidence-button' in changed_id:
        return [compute_options_for_applications()]
    elif 'filter-evidence-apps-button-1' in changed_id:
        query = 'SELECT app_id, app_name FROM selected_app WHERE app_id IN (SELECT app_id FROM app_paper)'
        results = do_query((), query)
        return [compute_list_of_dictionary_label_value(results)]
    else:
        return [compute_options_for_applications()]


@app.callback([dash.Output(component_id='pie_graph_evidence_div', component_property='children')],
              [dash.Input(component_id='app_evidence_dropdown', component_property='value')])
def recompute_pie_graph_evidence_app(app_name):
    if app_name is not None:
        return [compute_evidence_graph(app_name)]
    else:
        return [compute_evidence_graph(None)]


if __name__ == '__main__':
    run_dash()
