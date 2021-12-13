from dash import dcc, dash
from dash import html
import dash_bootstrap_components as dbc
from pandas import DataFrame
from DataManagers.DatabaseManager import do_query
from Utilities.Classifiers.LogRegClassifier import retrieve_columns_names_given_table


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


def extract_categories_distribution_from_database():
    query = "SELECT app_id, app_name, description, category_id, score, rating, installs, developer_id, " \
            "last_update, content_rating, content_rating_description, teacher_approved FROM selected_app"
    selected_app_table = do_query((), query)
    column_names_list = retrieve_columns_names_given_table("selected_app")

    df = create_dataframe_from_table(selected_app_table, column_names_list)
    return df


def extract_papers_data_from_database():
    query = "SELECT paper_id, paper_title, abstract, type FROM paper"
    paper_table = do_query((), query)
    study_types_list = ["RCT", "CaseControl", "CohortStudy", "SystematicReview", "ObservationalStudy", "MetaAnalysis"]
    study_types_occurrence_list = [0, 0, 0, 0, 0, 0]
    for row in paper_table:
        study_type = row[3]
        index = study_types_list.index(study_type)
        study_types_occurrence_list[index] = study_types_occurrence_list[index] + 1
    return study_types_list, study_types_occurrence_list


def create_pie_graph_study_type():
    study_types_list, study_types_occurrence_list = extract_papers_data_from_database()
    layout1 = html.Div([html.H1("Pie Graph"),
                        dcc.Graph(
                            id="example1",
                            figure={
                                'data': [
                                    {'values': study_types_occurrence_list,
                                     'labels': study_types_list,
                                     'type': 'pie',
                                     'name': 'Ships'}
                                ],
                                'layout': {
                                    'title': 'Study type distribution'
                                }
                            }
                        )
                        ])
    return layout1


def create_dash(app_):
    # df = pd.DataFrame(data=extract_papers_data_from_database())
    # app = dash.Dash(__name__)
    layout1 = create_pie_graph_study_type()

    # app.layout = html.Div([ layout1,layout2, layout1])
    app_.layout = html.Div([
        dbc.Col([
            html.H1("TITLE"),
            dbc.Row([
                dbc.Col(layout1, width=True)

            ])
        ])
    ])


if __name__ == '__main__':
    external_stylesheets = [dbc.themes.BOOTSTRAP]
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    create_dash(app)
    app.run_server(debug=True)
