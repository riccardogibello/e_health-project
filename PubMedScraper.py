from pymed import PubMed
from DataManagers.DatabaseManager import do_query


def find_apps_evidence():
    query = 'SELECT app_id, app_name FROM selected_app'
    app_name_list = do_query('', query)

    for app_name_sublist in app_name_list:
        app_id = app_name_sublist[0]
        app_name = app_name_sublist[1]
        papers = find_app_related_papers(
            app_name)  # list of dictionaries, each one containing the information about a paper

        if len(papers):
            for paper in papers:
                query = 'INSERT IGNORE INTO paper_app VALUES (%s, %s)'
                do_query((app_id, paper.get('pubmed_id')), query)

                query = 'INSERT IGNORE INTO paper VALUES (%s, %s)'
                do_query((paper.get('pubmed_id'), paper.get('title')), query)


def find_app_related_papers(app_name):
    pubmed = PubMed(tool='ehealth_group07', email='riccardo.gibello@mail.polimi.it')
    results = pubmed.query(app_name, max_results=100)

    article_list = []
    article_info = []

    for article in results:
        # Print the type of object we've found (can be either PubMedBookArticle or PubMedArticle).
        # We need to convert it to dictionary with available function
        article_dict = article.toDict()
        article_list.append(article_dict)

    # Generate list of dict records which will hold all article details that could be fetch from PUBMED API
    for article in article_list:
        # Sometimes article['pubmed_id'] contains list separated with comma - take first pubmedId in that list -
        # that's article pubmedId
        pubmed_id = article['pubmed_id'].partition('\n')[0]
        # Append article info to dictionary
        article_info.append({u'pubmed_id': pubmed_id,
                             u'title': article['title'],
                             u'keywords': article['keywords'],
                             u'journal': article['journal'],
                             u'abstract': article['abstract'],
                             u'conclusions': article['conclusions'],
                             u'methods': article['methods'],
                             u'results': article['results'],
                             u'copyrights': article['copyrights'],
                             u'doi': article['doi'],
                             u'publication_date': article['publication_date'],
                             u'authors': article['authors']})

    return article_info


if __name__ == '__main__':
    find_apps_evidence()
