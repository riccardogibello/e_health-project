class Publication:
    def __init__(self, title, abstract, authors, journal, nature_type):
        self.id = 0  # this is the mysql autogenerated id
        self.title = ''
        self.abstract = ''
        self.journal = ''
        self.nature_type = ''
        self.cited_apps = []
        self.authors = []

        if title:
            self.title = str(title.encode('ascii', errors='ignore').decode())
        if abstract:
            self.abstract = str(abstract.encode('ascii', errors='ignore').decode())
        if journal:
            self.journal = str(journal.encode('ascii', errors='ignore').decode())
        if nature_type:
            self.nature_type = str(nature_type.encode('ascii', errors='ignore').decode())
        self.authors = authors

    def add_cited_app(self, application):
        for app in self.cited_apps:
            if app.app_id == application.app_id:
                return
        self.cited_apps.append(application)
