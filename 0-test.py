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
from actions import *

utils = Utils()
app = Flask(__name__)

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
    """Triggar the test when post request is sent from jumpscalex repo.
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

                job = q.enqueue_call(func=build_and_test, args=(id,), result_ttl=5000)
                return job.get_id(), 200

    return "Done", 201


@app.route("/mintor")
def mintor():
    reboot = request.args.get("reboot")
    if reboot == "True":
        os.system("reboot")
    return str(os.getloadavg()), "200"


@app.route("/home")
def home():
    result = {"repos": [], "projects": []}
    for repo in utils.repo:
        repo_runs = RepoRun.objects(repo=repo)
        repo_name = repo.split("/")[-1]
        result["repos"].append({"repo_name": repo_name, "branches": []})

        branches = []
        for repo_run in repo_runs:
            if repo_run.branch in branches:
                continue
            else:
                branches.append(repo_run.branch)

        for branch in branches:
            repo_runs = RepoRun.objects(repo=repo, branch=branch).order_by("-timestamp")
            details = []
            for repo_run in repo_runs:
                details.append(
                    {
                        "commit": repo_run.commit,
                        "committer": repo_run.committer,
                        "timestamp": repo_run.timestamp,
                        "status": repo_run.status,
                        "result": repo_run.result,
                    }
                )
            result["repos"][0]["branches"].append({"branch_name": branch, "details": details})

    projects_name = []
    projects = ProjectRun.objects()
    for project in projects:
        if project.name in projects_name:
            continue
        else:
            projects_name.append(project.name)

    for project in projects_name:
        project_runs = ProjectRun.objects(name=project).order_by("-timestamp")
        details = []
        for project_run in project_runs:
            details.append(
                {"timestamp": project_run.timestamp, "status": project_run.status, "result": project_run.result}
            )
        result["projects"].append({"name": project, "details": details})

    result_json = json.dumps(result)
    return result_json, 200


@app.route("/status")
def status():
    project = request.args.get("project")
    repo = request.args.get("repo")
    branch = request.args.get("branch")
    file = request.args.get("file")
    if project:
        project_runs = ProjectRun.objects(name=project).order_by("-timestamp")
        for project_run in project_runs:
            if project_run.status is not "pending":
                if project_run.status == "success":
                    return send_file("{}_passing.svg".format(project), mimetype="image/svg+xml")
                else:
                    return send_file("{}_failing.svg".format(project), mimetype="image/svg+xml")
    elif repo:
        if not branch:
            branch = "master"
        repo_runs = RepoRun.objects(repo=repo, branch=branch).order_by("-timestamp")
        for repo_run in repo_runs:
            if repo_run.status is not "pending":
                if repo_run.status == "success":
                    return send_file("build_passing.svg", mimetype="image/svg+xml")
                else:
                    return send_file("build_failing.svg", mimetype="image/svg+xml")

    return abort(404)


if __name__ == "__main__":
    port = int(utils.serverip.split(":")[-1])
    app.run("0.0.0.0", port)
