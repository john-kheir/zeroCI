import mongoengine
from mongoengine import fields, Document


class RepoRun(Document):
    timestamp = fields.FloatField(required=True)
    status = fields.StringField(min_length=5, max_length=7, default="pending", required=True)
    repo = fields.StringField()
    branch = fields.StringField(required=True)
    commit = fields.StringField()
    committer = fields.StringField()
    result = fields.ListField(default=[])

    meta = {"collection": "repo"}


class ProjectRun(Document):
    timestamp = fields.FloatField(required=True)
    status = fields.StringField(min_length=5, max_length=7, default="pending", required=True)
    name = fields.StringField()
    result = fields.ListField(default=[])

    meta = {"collection": "project"}
