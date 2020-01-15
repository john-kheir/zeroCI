from mongoengine import fields, Document, connect

from utils.config import Configs


class RepoRun(Document):
    timestamp = fields.FloatField(required=True)
    status = fields.StringField(min_length=5, max_length=7, default="pending", required=True)
    repo = fields.StringField()
    branch = fields.StringField(required=True)
    commit = fields.StringField()
    committer = fields.StringField()
    result = fields.ListField(default=[])

    meta = {"collection": "repo", "indexes": ["timestamp"]}


class ProjectRun(Document):
    timestamp = fields.FloatField(required=True)
    status = fields.StringField(min_length=5, max_length=7, default="pending", required=True)
    name = fields.StringField()
    result = fields.ListField(default=[])

    meta = {"collection": "project", "indexes": ["timestamp"]}


class DB(Configs):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_connect()

    def db_connect(self):
        connect(db=self.db_name, host=self.db_host, port=self.db_port)
