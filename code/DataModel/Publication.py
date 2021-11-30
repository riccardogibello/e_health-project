class Publication:
    title = ''
    abstract = ''
    authors = []
    cited_apps = []

    def __init__(self, title, abstract, authors):
        if title:
            self.title = str(title.encode('ascii', errors='ignore').decode())
        if abstract:
            self.abstract = str(abstract.encode('ascii', errors='ignore').decode())
        self.authors = authors

    def add_cited_app(self, application):
        for app in self.cited_apps:
            if app.app_id == application.app_id:
                return
        self.cited_apps.append(application)
