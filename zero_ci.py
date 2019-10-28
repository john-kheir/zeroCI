from datetime import datetime
import os
import json

from flask import Flask, request, send_file, render_template, abort, Response, redirect
from rq import Queue
from rq.job import Job
from flask_cors import CORS
from rq_scheduler import Scheduler
from redis import Redis

from .utils.config import Configs
from .github.github import Github
from .rq.worker import conn
from .actions import Actions
from .mongo.db import *


configs = Configs()
actions = Actions()
github = Github()
DB()

app = Flask(__name__, static_folder="./dist/static", template_folder="./dist")

CORS(app, resources={r"/*": {"origins": "*"}})

q = Queue(connection=conn)
scheduler = Scheduler(connection=Redis())


@app.after_request
def set_response_headers(response):
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/trigger", methods=["POST"])
def trigger(**kwargs):
    """Trigger the test when a post request is sent from a repo's webhook.
    """
    if request.headers.get("Content-Type") == "application/json":
        # push case
        reference = request.json.get("ref")
        if reference:
            repo = request.json["repository"]["full_name"]
            branch = reference.split("/")[-1]
            commit = request.json["after"]
            committer = request.json["pusher"]["name"]
            deleted = request.json["deleted"]
            if repo in configs.repos and deleted == False:
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
                github.github_status_send(status=status, link=configs.domain, repo=repo, commit=commit)

                job = q.enqueue_call(func=actions.build_and_test, args=(id,), result_ttl=5000, timeout=20000)
                return Response(job.get_id(), 200)

    return Response("Done", 200)


@app.route("/api/add_project", methods=["POST"])
def add_project():
    if request.headers.get("Content-Type") == "application/json":
        project_name = request.json.get("project_name")
        prequisties = request.json.get("prequisties")
        install_script = request.json.get("install_script")
        test_script = request.json.get("test_script")
        run_time = request.json.get("run_time")
        authentication = request.json.get("authentication")
        timeout = request.json.get("timeout", 3600)
        if authentication == configs.github_token:
            if not (
                isinstance(project_name, str)
                and isinstance(install_script, (str, list))
                and isinstance(test_script, (str, list))
                and isinstance(prequisties, (str, list))
                and isinstance(run_time, str)
                and isinstance(timeout, int)
            ):
                return Response("Wrong data", 400)

            if isinstance(install_script, list):
                install_script = " && ".join(install_script)

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


@app.route("/api/remove_project", methods=["POST"])
def remove_project():
    if request.headers.get("Content-Type") == "application/json":
        project_name = request.json.get("project_name")
        authentication = request.json.get("authentication")
        if authentication == configs.github_token:
            scheduler.cancel(project_name)
        return "Removed", 200


@app.route("/api/")
def home():
    """Return repos and projects which are running on the server.
    """
    result = {"repos": [], "projects": []}
    result["repos"] = RepoRun.objects.distinct("repo")
    result["projects"] = ProjectRun.objects.distinct("name")
    result_json = json.dumps(result)
    return result_json, 200


@app.route("/api/repos/<path:repo>")
def branch(repo):
    """Returns tests ran on this repo with specific branch or test details if id is sent.

    :param repo: repo's name
    :param branch: the branch's name in the repo
    :param id: DB id of test details.
    """
    branch = request.args.get("branch")
    id = request.args.get("id")

    if id:
        repo_run = RepoRun.objects.get(id=id, repo=repo)
        result = json.dumps(repo_run.result)
        return result
    if branch:
        fields = ["status", "commit", "committer", "timestamp"]
        repo_runs = RepoRun.objects(repo=repo, branch=branch).only(*fields).order_by("-timestamp")
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


@app.route("/api/projects/<project>")
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

    fields = ["status", "timestamp"]
    project_runs = ProjectRun.objects(name=project).only(*fields).order_by("-timestamp")
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
    result = request.args.get("result")  # to return the run result
    fields = ["status"]
    if project:
        project_run = (
            ProjectRun.objects(name=project, status__ne="pending").only(*fields).order_by("-timestamp").first()
        )
        if result:
            link = f"{configs.domain}/projects/{project}?id={str(project_run.id)}"
            return redirect(link)
        if project_run.status == "success":
            return send_file("svgs/build_passing.svg", mimetype="image/svg+xml")
        else:
            return send_file("svgs/build_failing.svg", mimetype="image/svg+xml")

    elif repo:
        if not branch:
            branch = "master"
        repo_run = (
            RepoRun.objects(repo=repo, branch=branch, status__ne="pending").only(*fields).order_by("-timestamp").first()
        )
        if result:
            link = f"{configs.domain}/repos/{repo.replace('/', '%2F')}/{branch}/{str(repo_run.id)}"
            return redirect(link)
        if repo_run.status == "success":
            return send_file("svgs/build_passing.svg", mimetype="image/svg+xml")
        else:
            return send_file("svgs/build_failing.svg", mimetype="image/svg+xml")

    return abort(404)


@app.route("/get_status")
def state():
    """Return the result of a run using id.
    """
    n = request.args.get("n")
    id = request.args.get("id")
    if not n:
        n = "1"
    if n.isnumeric():
        if id:
            try:
                repo_run = RepoRun.objects.get(id=id)
            except:
                try:
                    repo_run = ProjectRun.objects.get(id=id)
                except:
                    return abort(404)
            if int(n) <= len(repo_run.result):
                result = repo_run.result[int(n) - 1]
                if result["type"] == "testsuite":
                    return render_template("template.html", **result["content"])
                else:
                    return render_template("result.html", content=result["content"])

    return abort(400)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return render_template("index.html")


if __name__ == "__main__":
    app.run("0.0.0.0", 6010)
