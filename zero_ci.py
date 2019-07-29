from flask import Flask, request, send_file, render_template, abort, redirect, Response
from utils import Utils
from datetime import datetime
from db import *
import os
import json
import atexit
from builders import builders
from rq import Queue
from rq.job import Job
from worker import conn
from actions import Actions
from flask_cors import CORS
from rq_scheduler import Scheduler
from redis import Redis

utils = Utils()
actions = Actions()

app = Flask(__name__)
CORS(app)

q = Queue(connection=conn)
scheduler = Scheduler(connection=Redis())


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

                job = q.enqueue_call(func=actions.build_and_test, args=(id,), result_ttl=5000, timeout=8000)
                return Response(job.get_id(), 200)

    return Response("Done", 200)


@app.route("/add_project", methods=["POST"])
def add_project():
    if request.headers.get("Content-Type") == "application/json":
        project_name = request.json.get("project_name")
        prequisties = request.json.get("prequisties")
        install_script = request.json.get("install_script")
        test_script = request.json.get("test_script")
        run_time = request.json.get("run_time")
        authentication = request.json.get("authentication")
        timeout = request.json.get("timeout", 3600)
        if authentication == utils.github_token:
            if not (
                isinstance(project_name, str)
                and isinstance(install_script, str)
                and isinstance(test_script, (str, list))
                and isinstance(prequisties, str)
                and isinstance(run_time, str)
                and isinstance(timeout, int)
            ):
                return Response("Wrong data", 400)

            if isinstance(test_script, str):
                test_script = [test_script]

            try:
                scheduler.cron(
                    cron_string=run_time,
                    func=actions.run_project,
                    args=[project_name, install_script, test_script, prequisties, timeout],
                    id=project_name,
                    timeout=timeout + 3600,
                )
            except:
                return Response("Wrong time format should be like (0 * * * *)", 400)
            return Response("Added", 200)
        else:
            return Response("Authentication failed", 400)
    return Response("", 404)


@app.route("/remove_project", methods=["POST"])
def remove_project():
    if request.headers.get("Content-Type") == "application/json":
        project_name = request.json.get("project_name")
        authentication = request.json.get("authentication")
        if authentication == utils.github_token:
            scheduler.cancel(project_name)
        return "Removed", 200


@app.route("/")
def home():
    """Return repos and projects which are running on the server.
    """
    result = {"repos": [], "projects": []}
    result["repos"] = RepoRun.objects.distinct("repo")
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
    if branch:
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
    branches = RepoRun.objects(repo=repo).distinct("branch")
    result = json.dumps(branches)
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
    # file = request.args.get("file")  # to return the run result
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


@app.route("/last_status")
def state():
    """Api for last status of the tests on branch development _jumpscale_testing.
    """
    repo_runs = RepoRun.objects(repo="threefoldtech/jumpscaleX", branch="development_jumpscale_testing").order_by(
        "-timestamp"
    )
    for repo_run in repo_runs:
        for result in repo_run.result:
            if result["type"] == "testsuite":
                return render_template("template.html", **result["content"])


if __name__ == "__main__":
    port = int(utils.serverip.split(":")[-1])
    app.run("0.0.0.0", port)
