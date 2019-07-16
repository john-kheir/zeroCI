from flask import Flask, request, send_file, render_template, abort, redirect
from utils import Utils
from datetime import datetime
from db import *
import os
import json
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from builders import builders
from rq import Queue
from rq.job import Job
from worker import conn
from actions import Actions
from flask_cors import CORS

utils = Utils()
actions = Actions()

app = Flask(__name__)
CORS(app)

q = Queue(connection=conn)

scheduler = BackgroundScheduler()
scheduler.add_job(func=builders, trigger="cron", hour=18)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.after_request
def set_response_headers(response):
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/triggar", methods=["POST"])
def triggar(**kwargs):
    """Triggar the test when a post request is sent from a repo's webhook.
    """
    if request.headers.get("Content-Type") == "application/json":
        # push case
        reference = request.json.get("ref")
        if reference:
            repo = request.json["repository"]["full_name"]
            branch = reference.split("/")[-1]
            commit = request.json["after"]
            committer = request.json["pusher"]["name"]
            if repo == utils.repo[0]:
                status = "pending"
                repo_run = RepoRun(
                    timestamp=datetime.now().timestamp(),
                    status=status,
                    repo=repo,
                    branch=branch,
                    commit=commit,
                    committer=committer,
                )
                repo_run.save()
                id = str(repo_run.id)
                utils.github_status_send(status=status, link=utils.serverip, repo=repo, commit=commit)

                job = q.enqueue_call(func=actions.build_and_test, args=(id,), result_ttl=5000, timeout=1800)
                return job.get_id(), 200

    return "Nothing to do", 201


@app.route("/")
def home():
    """Return repos and projects which are running on the server.
    """
    result = {"repos": [], "projects": []}
    repos = []
    repos = RepoRun.objects.distinct("repo")
    for repo in repos:
        branches = RepoRun.objects(repo=repo).distinct("branch")
        result["repos"].append({repo: branches})
    result["projects"] = ProjectRun.objects.distinct("name")
    result_json = json.dumps(result)
    return result_json, 200


@app.route("/repos/<path:repo>")
def branch(repo):
    """Returns tests ran on this repo with specific branch or test details if id is sent.

    :param repo: repo's name
    :param branch: the branch's name in the repo
    :param id: DB id of test details.
    """
    branch = request.args.get("branch")
    id = request.args.get("id")
    if not branch:
        return abort(400)
    else:
        if id:
            repo_run = RepoRun.objects.get(id=id, repo=repo, branch=branch)
            result = json.dumps(repo_run.result)
            return result

        repo_runs = RepoRun.objects(repo=repo, branch=branch).order_by("-timestamp")
        details = []
        for repo_run in repo_runs:
            details.append(
                {
                    "commit": repo_run.commit,
                    "committer": repo_run.committer,
                    "timestamp": repo_run.timestamp,
                    "status": repo_run.status,
                    "id": str(repo_run.id),
                }
            )
        result = json.dumps(details)
        return result


@app.route("/projects/<project>")
def project(project):
    """Returns tests ran on this project or test details if id is sent.

    :param project: project's name
    :param id: DB id of test details.
    """
    id = request.args.get("id")
    if id:
        project_run = ProjectRun.objects.get(id=id)
        result = json.dumps(project_run.result)
        return result

    project_runs = ProjectRun.objects(name=project).order_by("-timestamp")
    details = []
    for project_run in project_runs:
        details.append({"timestamp": project_run.timestamp, "status": project_run.status, "id": str(project_run.id)})
    result = json.dumps(details)
    return result


@app.route("/status")
def status():
    """Returns repo's branch or project status for github.
    """
    project = request.args.get("project")
    repo = request.args.get("repo")
    branch = request.args.get("branch")
    file = request.args.get("file")  # to return the run result
    if project:
        project_run = ProjectRun.objects(name=project, status__ne="pending").order_by("-timestamp").first()
        if project_run.status == "success":
            return send_file("{}_passing.svg".format(project), mimetype="image/svg+xml")
        else:
            return send_file("{}_failing.svg".format(project), mimetype="image/svg+xml")

    elif repo:
        if not branch:
            branch = "master"
        repo_run = RepoRun.objects(repo=repo, branch=branch, status__ne="pending").order_by("-timestamp")
        if repo_run.status == "success":
            return send_file("build_passing.svg", mimetype="image/svg+xml")
        else:
            return send_file("build_failing.svg", mimetype="image/svg+xml")

    return abort(404)


if __name__ == "__main__":
    port = int(utils.serverip.split(":")[-1])
    app.run("0.0.0.0", port)
