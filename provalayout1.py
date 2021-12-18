from dash import dcc, dash
from dash import html
import dash_bootstrap_components as dbc
from pandas import DataFrame
from DataManagers.DatabaseManager import do_query, retrieve_columns_names_given_table
import plotly.express as px


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


def get_selected_app_data_dataframe_from_database():
    query = "SELECT app_id, app_name, description, category_id, score, rating, installs, developer_id, " \
            "last_update, content_rating, content_rating_description, teacher_approved FROM selected_app"
    selected_app_table = do_query((), query)
    column_names_list = retrieve_columns_names_given_table("selected_app")

    df = create_dataframe_from_table(selected_app_table, column_names_list)
    return df


def get_papers_data_as_dataframe_from_database():
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
    study_types_list, study_types_occurrence_list = get_papers_data_as_dataframe_from_database()
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


def create_bar_plot_categories_into_selected_app():
    # create a dataframe that contains all the selected_app data
    dataframe_selected_app = get_selected_app_data_dataframe_from_database()
    # create a new dataframe that contains only the interesting data (here the category_id)
    dataframe_selected_app_filtered = DataFrame(dataframe_selected_app.loc[:, 'category_id'])
    # add a new column to the dataframe called 'occurrence'. All the rows will contain a 1.
    # This is used in the following the group by.
    dataframe_selected_app_filtered['occurrence'] = '1'

    # Here all the category_id are grouped and the 'occurrence' values are summed. In this way the dataframe will
    # contain for each category_id the total number of occurrences of that category_id.
    dataframe_selected_app_filtered = dataframe_selected_app_filtered.groupby('category_id').count().reset_index()

    fig = px.bar(dataframe_selected_app_filtered, x='category_id', y='occurrence')

    layout2 = html.Div([html.H1("Bar Plot"),
                        dcc.Graph(
                            id='example-graph',
                            figure=fig
                        )
                        ])
    return layout2


def create_dash(app_):
    # df = pd.DataFrame(data=extract_papers_data_from_database())
    # app = dash.Dash(__name__)
    layout1 = create_pie_graph_study_type()

    layout2 = create_bar_plot_categories_into_selected_app()

    # app.layout = html.Div([ layout1,layout2, layout1])
    app_.layout = html.Div([
        dbc.Col([
            html.H1("TITLE"),
            dbc.Row([
                dbc.Col(layout1),
                dbc.Col(layout2)
            ])
        ])
    ])


if __name__ == '__main__':
    external_stylesheets = [dbc.themes.BOOTSTRAP]
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    create_dash(app)
    app.run_server(debug=True)
