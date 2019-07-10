from autotest import RunTests
from build_image import BuildImage
from utils import Utils
from db import *

utils = Utils()


def test_run(image_name, id):
    """Run test aginst the new commit and give report on Telegram chat and github commit status.
    
    :param image_name: docker image name.
    :type image_name: str
    :param repo: full repo name
    :type repo: str
    :param branch: branch name.
    :type branch: str
    :param commit: commit hash.
    :type commit: str
    :param committer: name of the committer on github.
    :type committer: str
    """
    repo_run = RepoRun.objects.get(id=id)
    test = RunTests()
    status = "success"
    content = test.github_get_content(repo=repo_run.repo, ref=repo_run.commit)
    if content:
        lines = content.splitlines()
        for i, line in enumerate(lines):
            status = "success"
            if line.startswith("#"):
                continue
            response, file_path = test.run_tests(image_name=image_name, run_cmd=line)
            if file_path:
                if response.returncode:
                    status = "failure"
                result = utils.xml_parse(path=file_path, line=line)
                repo_run.result.append(
                    {"type": "testsuite", "status": status, "name": result["summary"]["name"], "content": result}
                )
            else:
                if response.returncode:
                    status = "failure"
                    name = "cmd {}".format(i + 1)
                repo_run.result.append({"type": "log", "status": status, "name": name, "content": response.stdout})
    else:

        repo_run.result.append({"type": "log", "status": status, "name": "No tests", "content": "No tests found"})
    repo_run.save()


def test_black(image_name, id):
    """Run test aginst the new commit and give report on Telegram chat and github commit status.

    :param image_name: docker image name.
    :type image_name: str
    :param repo: full repo name
    :type repo: str
    :param branch: branch name.
    :type branch: str
    :param commit: commit hash.
    :type commit: str
    """
    repo_run = RepoRun.objects.get(id=id)
    test = RunTests()
    link = test.serverip
    status = "success"
    line = "black {} -l 120 -t py37 --exclude 'templates'".format(utils.project_path)
    response, file = test.run_tests(image_name=image_name, run_cmd=line)
    if "reformatted" in response.stdout:
        status = "failure"
    repo_run.result.append({"type": "log", "status": status, "name": "Black Formatting", "content": response.stdout})
    repo_run.save()
    test.github_status_send(
        status=status, link=link, repo=repo_run.repo, commit=repo_run.commit, context="Black-Formatting"
    )


def build_image(branch, commit, id):
    """Build a docker image to install application.

    :param branch: branch name.
    :type branch: str
    :param commit: commit hash.
    :type commit: str
    :param committer: name of the committer on github.
    :type committer: str
    """
    build = BuildImage()
    image_name = build.random_string()
    response = build.image_bulid(image_name=image_name, file="Dockerfile", branch=branch, commit=commit)
    if response.returncode:
        build.images_clean()
        repo_run = RepoRun.objects(id=id).first()
        repo_run.status = "error"
        repo_run.result.append({"type": "log", "status": "error", "content": response.stdout})
        repo_run.save()
        utils.report(id=id)
        return False
    return image_name


def cal_status(id):
    repo_run = RepoRun.objects.get(id=id)
    status = "success"
    for result in repo_run.result:
        if result["status"] != "success":
            status = result["status"]
    repo_run.status = status
    repo_run.save()


def build_and_test(id):
    repo_run = RepoRun.objects.get(id=id)
    image_name = build_image(branch=repo_run.branch, commit=repo_run.commit, id=id)
    if image_name:
        test_black(image_name=image_name, id=id)
        test_run(image_name=image_name, id=id)
        cal_status(id=id)
        utils.report(id=id)
        build = BuildImage()
        build.images_clean(image_name=image_name)
