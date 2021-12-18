import numpy as np
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from pandas import DataFrame
import plotly.express as px
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
    # TODO: add content_rating_description
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
        "Type": ['App', 'Selected App', 'App with scientific evidence'],
        "Occurrence": [len_app, len_selected_app, len_cited_apps],
        "Legend": ["App", "Selected_App", "App_Paper"]
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
    dataframe_selected_app_categories_list, dataframe_selected_app_occurrence_list = create_bar_plot_categories_into_selected_app()
    dataframe_app_categories_list, dataframe_app_occurrence_list = create_bar_plot_categories_into_app()

    for elem in dataframe_selected_app_categories_list:
        dataframe_app_categories_list.append(elem)

    for elem in dataframe_selected_app_occurrence_list:
        dataframe_app_occurrence_list.append(elem)

    df = pd.DataFrame({
        "Category": dataframe_app_categories_list,
        "Occurrence": dataframe_app_occurrence_list,
        "Type": ["App", "App", "App", "App", "App", "App", "App", "App", "App", "App", "App", "App", "App", "App",
                 "Selected_App", "Selected_App", "Selected_App", "Selected_App", "Selected_App", "Selected_App",
                 "Selected_App",
                 "Selected_App", "Selected_App", "Selected_App", "Selected_App", "Selected_App", "Selected_App",
                 "Selected_App"]
    })

    fig = px.bar(df, x="Category", y="Occurrence", color="Type", barmode="group", log_y=True)

    return fig


def get_overview_dash_page():
    colors = {
        'background': '#34568b',
        'text': '#000000'
    }

    # this computes a histogram containing the number of starting apps, the number of serious games selected
    # and the number of apps with evidence
    df = get_dataframe_for_histogram_apps__sel_apps__evidence_apps()
    hist_app__sel_app__ev_apps = px.bar(df, x="Type", y="Occurrence", log_y=True, color="Legend", barmode="group")

    # this computes the study_type distribution that is used to populate a pie graph
    study_types_list, study_types_occurrence_list = get_papers_data_as_dataframe_from_database()

    # this computes a bar plot to show the distribution of the categories of apps in the starting set of apps
    app__sel_apps__hist = create_fig_categories_into_app()

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
                               'background': '#ADD8E6'},
                        children=[
                            html.Tr(
                                children=[
                                    html.Td(
                                        dcc.Graph(
                                            id='ase_hist',
                                            figure=hist_app__sel_app__ev_apps
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
                                                ],
                                                'layout': {
                                                    'title': 'Study type distribution',
                                                }
                                            }
                                        )
                                    ),
                                ]
                            )
                        ]
                    )
                ], style={'text-align': 'center', 'display': 'flex', 'justify-content': 'center'}
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
                                children='Dash: Categories in App and Selected_App.',
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
                               'margin-left': 'auto',
                               'margin-right': 'auto',
                               'margin-top': '50px',
                               'margin-bottom': '50px',
                               'background': '#ADD8E6',
                               'display': 'table',
                               'min-width': '500px'
                               },
                        children=[],
                    )
                ],
                style={'text-align': 'center', 'display': 'flex', 'justify-content': 'center'}
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
