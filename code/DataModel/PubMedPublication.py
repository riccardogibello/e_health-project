from DataModel.Publication import Publication


class PubMedPublication(Publication):
    def __init__(self, title, abstract, authors, pubmed_id):
        super().__init__(title, abstract, authors, '', '')
        self.pubmed_id = pubmed_id
