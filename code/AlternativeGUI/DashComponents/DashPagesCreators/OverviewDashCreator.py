import pandas as pd
from dash import html, dcc
from pandas import DataFrame
import plotly.express as px

from AlternativeGUI.DashComponents.DashPagesCreators.SpecificDashCreator import compute_options_for_applications
from DataManagers.DatabaseManager import do_query, retrieve_columns_names_given_table


def create_dataframe_from_table(table, columns):
    dictionary = {}
    for column in columns:
        dictionary.__setitem__(column, [])

    for row in table:
        for i in range(len(columns)):
            column = columns[i]
            dictionary.get(column).append(row[i])

    dataframe = DataFrame.from_dict(data=dictionary)
    return dataframe


def get_papers_data_as_dataframe_from_database():
    query = "SELECT paper_id, paper_title, abstract, type FROM paper"
    paper_table = do_query((), query)
    study_types_list = ["RCT", "Case Control", "Cohort Study", "Systematic Review", "Observational Study",
                        "Meta Analysis"]
    study_types_occurrence_list = [0, 0, 0, 0, 0, 0]
    for row in paper_table:
        study_type = row[3]
        index = study_types_list.index(study_type)
        study_types_occurrence_list[index] = study_types_occurrence_list[index] + 1
    return study_types_list, study_types_occurrence_list


def create_bar_plot_categories_into_selected_app():
    dataframe_selected_app = get_selected_app_data_dataframe_from_database()
    dataframe_selected_app_filtered = DataFrame(dataframe_selected_app.loc[:, 'category_id'])
    dataframe_selected_app_filtered['occurrence'] = '1'
    dataframe_selected_app_filtered_count = dataframe_selected_app_filtered.groupby('category_id').count().reset_index()

    dataframe_selected_app_categories_list = dataframe_selected_app_filtered_count['category_id'].tolist()
    dataframe_selected_app_occurrence_list = dataframe_selected_app_filtered_count['occurrence'].tolist()
    return dataframe_selected_app_categories_list, dataframe_selected_app_occurrence_list


def get_app_paper_data_dataframe_from_database():
    query = "SELECT paper_id, app_id FROM app_paper"
    app_paper_table = do_query((), query)
    column_names_list = retrieve_columns_names_given_table("app_paper")
    df = create_dataframe_from_table(app_paper_table, column_names_list)

    df = DataFrame(df.loc[:, 'app_id'])
    df = df.drop_duplicates(subset=["app_id"])

    return df


def get_selected_app_data_dataframe_from_database():
    query = "SELECT app_id, app_name, description, category_id, score, rating, installs, developer_id, " \
            "last_update, content_rating, teacher_approved FROM selected_app"

    selected_app_table = do_query((), query)
    column_names_list = retrieve_columns_names_given_table("selected_app")
    df = create_dataframe_from_table(selected_app_table, column_names_list)
    return df


def get_app_data_dataframe_from_database():
    query = "SELECT app_id, app_name, description, category_id, score, rating, installs, developer_id, " \
            "last_update, content_rating, teacher_approved FROM app"
    app_table = do_query((), query)
    column_names_list = retrieve_columns_names_given_table("app")
    df = create_dataframe_from_table(app_table, column_names_list)
    return df


def get_dataframe_for_histogram_apps__sel_apps__evidence_apps():
    dataframe_app_paper = get_app_paper_data_dataframe_from_database()
    len_cited_apps = len(dataframe_app_paper.index)
    dataframe_selected_app = get_selected_app_data_dataframe_from_database()
    len_selected_app = len(dataframe_selected_app)
    dataframe_app = get_app_data_dataframe_from_database()
    len_app = len(dataframe_app)

    df = pd.DataFrame({
        "Type": ['(a)', '(b)', '(c)'],
        "Occurrences": [len_app, len_selected_app, len_cited_apps],
        "Legend": ["Total games \non Play Store", "Total serious games for\nchildren on Play Store",
                   "Total serious games with\nevidence on Play Store"]
    })

    return df


def get_dataframe_for_histogram_teacher_approved_apps():
    query = 'SELECT COUNT(*) from app WHERE teacher_approved = True'
    n_apps_ta = do_query((), query)[0][0]
    query = 'SELECT COUNT(*) from selected_app WHERE teacher_approved = True'
    n_sel_apps_ta = do_query((), query)[0][0]
    query = 'SELECT COUNT(*) from selected_app AS sa WHERE teacher_approved = True AND sa.app_id IN (' \
            'SELECT ap.app_id FROM app_paper AS ap)'
    n_evidence_ta = do_query((), query)[0][0]

    df = pd.DataFrame({
        "Type": ['(a)', '(b)', '(c)'],
        "Occurrences": [n_apps_ta, n_sel_apps_ta, n_evidence_ta],
        "Legend": ["Play Store games TA", "Serious games for children on Play Store TA",
                   "TA serious games with evidence on Play Store"]
    })

    return df


def create_bar_plot_categories_into_app():
    dataframe_app = get_app_data_dataframe_from_database()
    dataframe_app_filtered = DataFrame(dataframe_app.loc[:, 'category_id'])
    dataframe_app_filtered['occurrence'] = '1'
    dataframe_app_filtered_count = dataframe_app_filtered.groupby('category_id').count().reset_index()

    dataframe_app_categories_list = dataframe_app_filtered_count['category_id'].tolist()
    dataframe_app_occurrence_list = dataframe_app_filtered_count['occurrence'].tolist()

    return dataframe_app_categories_list, dataframe_app_occurrence_list


def create_fig_categories_into_app():
    dataframe_selected_app_categories_list, dataframe_selected_app_occurrence_list = \
        create_bar_plot_categories_into_selected_app()
    dataframe_app_categories_list, dataframe_app_occurrence_list = create_bar_plot_categories_into_app()
    color_labels = []

    for i in range(len(dataframe_app_categories_list)):
        color_labels.append('Generic games on Play Store')

    for elem in dataframe_selected_app_categories_list:
        color_labels.append('Serious games on Play Store')
        dataframe_app_categories_list.append(elem)

    for elem in dataframe_selected_app_occurrence_list:
        dataframe_app_occurrence_list.append(elem)

    df = pd.DataFrame({
        "Category": dataframe_app_categories_list,
        "Occurrences": dataframe_app_occurrence_list,
        "Type": color_labels
    })

    fig = px.bar(df, x="Category", y="Occurrences", color="Type", barmode="group", log_y=True)

    return fig


def compute_evidence_graph(app_id):
    study_type__list = []
    study_type_values__list = []

    query = 'SELECT p.type, count(*) FROM app_paper AS ap, paper AS p WHERE ap.paper_id = p.paper_id'
    if app_id:
        query = query + ' AND ap.app_id = %s'
    query = query + ' GROUP BY p.type;'
    if app_id:
        results = do_query((app_id,), query)
    else:
        results = do_query((), query)
    for result in results:
        study_type__list.append(result[0])
        study_type_values__list.append(result[1])

    return dcc.Graph(
        figure={
            'data': [
                {'values': study_type_values__list,
                 'labels': study_type__list,
                 'type': 'pie',
                 'name': 'Ships'}
            ]
        },
        style={'width': '60%', 'margin-left': 'auto', 'margin-right': 'auto'}
    )


def compute_teacher_approved_hist():
    df = get_dataframe_for_histogram_teacher_approved_apps()
    hist_teacher_approved = px.bar(df, x="Type", y="Occurrences", log_y=True, color="Legend", barmode="group")
    hist_teacher_approved.update_layout(legend=dict(x=0.5, y=1)
                                        )
    return hist_teacher_approved


def compute_teacher_approved_pie():
    query = 'SELECT COUNT(*) FROM app WHERE teacher_approved = True'
    n_app_ta = int(do_query((), query)[0][0])
    query = 'SELECT COUNT(*) FROM selected_app WHERE teacher_approved = True'
    n_sel_ta = int(do_query((), query)[0][0])
    n_nser_ta = n_app_ta - n_sel_ta

    labels = ['TA non-serious', 'TA serious']
    values = [n_nser_ta, n_sel_ta]

    return {
        'data': [
            {'values': values,
             'labels': labels,
             'type': 'pie',
             'name': 'Ships'}
        ]
    }


def get_overview_dash_page():
    # this computes a histogram containing the number of starting apps, the number of serious games selected
    # and the number of apps with evidence
    df = get_dataframe_for_histogram_apps__sel_apps__evidence_apps()
    hist_app__sel_app__ev_apps = px.bar(df, x="Type", y="Occurrences", log_y=True, color="Legend", barmode="group")
    hist_app__sel_app__ev_apps.update_layout(legend=dict(x=0.5, y=1)
                                             )

    # this computes the study_type distribution that is used to populate a pie graph
    study_types_list, study_types_occurrence_list = get_papers_data_as_dataframe_from_database()

    # this computes a bar plot to show the distribution of the categories of apps in the starting set of apps
    app__sel_apps__hist = create_fig_categories_into_app()

    applications = compute_options_for_applications()

    evidence_graph = compute_evidence_graph(None)

    hist_apps_sel_apps_teacherappr = compute_teacher_approved_hist()

    pie_graph_teacher_approved = compute_teacher_approved_pie()

    layout = html.Div(
        children=[
            html.Table(
                children=[
                    html.Tr(html.Td(dcc.Link('Go back', href='/'),
                                    style={'padding': '10px'}))],
                style={'border': 'solid 2px',
                       'border-radius': '10px',
                       'margin-right': '10px',
                       'margin-left': 'auto',
                       'display': 'inline-block',
                       'background': '#ADD8E6'}
            ),
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
                               'width': '100%'},
                        children=[
                            html.Tr(children=[
                                html.Td(
                                    children='Apps vs. Serious Apps',
                                    style={'font-weight': 'bold', 'width': '50%'}),
                                html.Td(
                                    children='Study type distribution',
                                    style={'font-weight': 'bold', 'width': '50%'}),
                            ]),
                            html.Tr(
                                children=[
                                    html.Td(
                                        dcc.Graph(
                                            id='ase_hist',
                                            figure=hist_app__sel_app__ev_apps,
                                            style={'width': '80%', 'margin-left': 'auto', 'margin-right': 'auto'}
                                        )
                                    ),
                                    html.Td(
                                        dcc.Graph(
                                            id="pie_graph_study_types",
                                            figure={
                                                'data': [
                                                    {'values': study_types_occurrence_list,
                                                     'labels': study_types_list,
                                                     'type': 'pie',
                                                     'name': 'Ships'}
                                                ]
                                            },
                                            style={'width': '80%', 'margin-left': 'auto', 'margin-right': 'auto'}
                                        )
                                    ),
                                ]
                            ),
                            html.Tr(children=[
                                html.Td(
                                    children='The bar plot above resprents in (a) the quantity of generic '
                                             'games applications retrieved from the Play Store '
                                             'through simple filters on the genre'
                                             'and addressed age which, in (b) the quantity of games classified'
                                             'as serious games by a classification algorithm trained on a manually'
                                             'classified set of applications, in (c) the number of games for which '
                                             'literature published on Nature was found.', ),
                                html.Td(
                                    children='In the above pie graph it is represented '
                                             'the distribution of the study types among '
                                             'which evidence has been searched for.'),
                            ]),
                        ]
                    )
                ], style={'text-align': 'center', 'display': 'flex', 'justify-content': 'center', 'width': '100%'}
            ),
            html.Div(
                children=[
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
                               'width': '100%'
                               },
                        children=[
                            html.Tr(
                                children='Category distributions: Games vs Serious Games',
                                style={'font-weight': 'bold'}
                            ),
                            html.Tr(
                                children=[
                                    html.Td(
                                        dcc.Graph(
                                            id='bar_plot_categs_apps',
                                            figure=app__sel_apps__hist
                                        )
                                    )
                                ]
                            )
                        ]
                    ),
                ],
                style={'text-align': 'center', 'display': 'flex', 'justify-content': 'center'}
            ),
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
                               'width': '100%'},
                        children=[
                            html.Tr(children=[
                                html.Td(
                                    children='Teacher approved apps in generic games, \nnon medical '
                                             'evidence based serious games and literature supported serious games',
                                    style={'font-weight': 'bold', 'width': '50%'}),
                                html.Td(
                                    children='How many Teacher Approved apps are Serious Games?',
                                    style={'font-weight': 'bold', 'width': '50%'}),
                            ]),
                            html.Tr(
                                children=[
                                    html.Td(
                                        dcc.Graph(
                                            id='apps_sel_apps_teacherappr_hist',
                                            figure=hist_apps_sel_apps_teacherappr,
                                            style={'width': '80%', 'margin-left': 'auto', 'margin-right': 'auto'}
                                        )
                                    ),
                                    html.Td(
                                        dcc.Graph(
                                            id="pie_graph_teacher_approved",
                                            figure=pie_graph_teacher_approved,
                                            style={'width': '80%', 'margin-left': 'auto', 'margin-right': 'auto'}
                                        )
                                    ),
                                ]
                            )
                        ]
                    )
                ], style={'text-align': 'center', 'display': 'flex', 'justify-content': 'center', 'width': '100%'}
            ),
            html.Div(
                children=[
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
                               'width': '100%',
                               'table-layout': 'fixed'
                               },
                        children=[
                            html.Tr(
                                html.Td(
                                    html.Div(
                                        children='Serious Games evidence on Play Store',
                                        style={'font-weight': 'bold', 'text-align': 'center'}
                                    ),
                                    colSpan=3
                                ),
                            ),
                            html.Tr(
                                children=[
                                    html.Td(
                                        dcc.Dropdown(
                                            id='app_evidence_dropdown',
                                            options=applications,
                                            placeholder="Write here the name of an application"),
                                        style={'width': '60%'}
                                    ),
                                    html.Td(
                                        html.Button('Filter apps with evidence', id='filter-evidence-apps-button-1')
                                    ),
                                    html.Td(
                                        html.Button('Reset filter', id='reset-evidence-button')
                                    )
                                ]
                            ),
                            html.Tr(
                                children=[
                                    html.Td(
                                        evidence_graph,
                                        id="pie_graph_evidence_div",
                                        colSpan=3
                                    )
                                ]
                            )
                        ]
                    ),
                ],
                style={'text-align': 'center', 'display': 'flex', 'justify-content': 'center'}
            )
        ], style={'background': '#34568b',
                  'margin-left': '20px',
                  'margin-right': '20px',
                  'margin-top': '17px',
                  'margin-bottom': '10px',
                  'border-radius': '20px',
                  'padding': '20px'}
    )

    return layout
