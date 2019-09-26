from subprocess import run, PIPE, Popen, TimeoutExpired, CompletedProcess
from uuid import uuid4
import configparser
import time
import os
import re
import codecs
import json
import base64
from telegram import Bot, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from github import Github
from mongoengine import connect
from db import *
import xmltodict
import yaml
import toml

ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


class Utils:
    def __init__(self):
        config = toml.load("config.toml")
        self.iyo_id = config["iyo"]["id"]
        self.iyo_secret = config["iyo"]["secret"]
        self.domain = config["main"]["domain"]
        self.result_path = config["main"]["result_path"]
        self.chat_id = config["telegram"]["chat_id"]
        self.bot_token = config["telegram"]["token"]
        self.github_token = config["github"]["token"]
        self.repo = config["github"]["repo"]
        self.db_name = config["db"]["name"]
        self.db_host = config["db"]["host"]
        self.db_port = config["db"]["port"]
        self.environment = config["environment"]
        self.github_cl = Github(self.github_token)
        self.telegram_cl = Bot(self.bot_token)
        self.db_connect(db_name=self.db_name, host=self.db_host, port=self.db_port)

    def db_connect(self, db_name, host, port):
        connect(db=db_name, host=host, port=port)

    def execute_cmd(self, cmd, timeout=3600):
        with Popen(cmd, shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE, encoding="utf-8") as process:
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                retruncode = process.poll()
            except TimeoutExpired:
                process.kill()
                stdout = "Error Timeout Exceeded {}".format(timeout)
                stderr = ""
                retruncode = 127

        return CompletedProcess(process.args, returncode=retruncode, stdout=stdout, stderr=stderr)

    def random_string(self):
        return str(uuid4())[:10]

    def send_msg(self, msg, link, repo=None, branch=None, commit=None, committer=None):
        """Send Telegram message using Telegram bot.

        :param msg: message to be sent.
        :type msg: str
        :param repo: full repo name
        :type repo: str
        :param branch: branch name
        :type branch: str
        :param commit: commit hash.
        :type commit: str
        :param committer: committer name on github.
        :type committer: str
        """
        if commit:
            msg = f"""{msg}
<a href="https://github.com/{repo}">{repo}</a>
{branch} <a href="https://github.com/{repo}/commit/{commit}">{commit[:7]}</a>
👤 <a href="https://github.com/{committer}">{committer}</a>"""

        button_list = [InlineKeyboardButton("Result", url=link)]
        reply_markup = InlineKeyboardMarkup([button_list])

        # msg = "\n".join([msg, repo, branch, committer, commit])
        for _ in range(0, 5):
            try:
                self.telegram_cl.send_message(
                    chat_id=self.chat_id,
                    text=msg,
                    reply_markup=reply_markup,
                    parse_mode="html",
                    disable_web_page_preview=True,
                )
                break
            except Exception:
                time.sleep(1)

    def write_file(self, text, file_name, file_path=""):
        """Write result file.

        :param text: text will be written to result file.
        :type text: str
        :param file_name: result file name.
        :type file_name: str
        """
        text = ansi_escape.sub("", text)
        if file_path == "":
            file_path = self.result_path
        file_path = os.path.join(file_path, file_name)
        if os.path.exists(file_path):
            append_write = "a"  # append if already exists
        else:
            append_write = "w"  # make a new file if not

        with codecs.open(file_path, append_write, "utf-8") as f:
            f.write(text + "\n")

    def github_status_send(
        self, status, link, repo, commit, description="JSX-machine for testing", context="continuous-integration/zeroCI"
    ):
        """Change github commit status.
        
        :param status: should be one of [error, failure, pending, success].
        :type status: str
        :param link: the result file link to be accessed through the server.
        :type link: str
        :param repo: full repo name
        :type repo: str
        :param commit: commit hash required to change its status on github.
        :type commit: str
        """
        for _ in range(0, 5):
            try:
                repo = self.github_cl.get_repo(repo)
                commit = repo.get_commit(commit)
                commit.create_status(state=status, target_url=link, description=description, context=context)
                break
            except Exception:
                time.sleep(1)

    def github_get_content(self, repo, ref, file_path="0-Test.sh"):
        """Get file content from github with specific ref.

        :param repo: full repo name
        :type repo: str
        :param ref: name of the commit/branch/tag.
        :type ref: str
        :param file_path: file path in the repo
        :type file_path: str
        """
        for _ in range(0, 5):
            try:
                repo = self.github_cl.get_repo(repo)
                content_b64 = repo.get_contents(file_path, ref=ref)
                break
            except Exception:
                time.sleep(1)
        else:
            return None
        content = base64.b64decode(content_b64.content)
        content = content.decode()
        return content

    def report(self, id):
        """Report the result to github commit status and Telegram chat.

        :param status: test status. 
        :type status: str
        :param file_name: result file name. 
        :type file_name: str
        :param repo: full repo name
        :type repo: str
        :param branch: branch name. 
        :type branch: str
        :param commit: commit hash.
        :type commit: str
        :param committer: committer name on github. 
        :type committer: str
        """
        repo_run = RepoRun.objects.get(id=id)
        link = f"{self.domain}/repos/{repo_run.repo.replace('/', '%2F')}/{repo_run.branch}/{str(repo_run.id)}"
        # link = f"{self.domain}/get_status?id={str(repo_run.id)}&n={len(repo_run.result)}"
        self.github_status_send(status=repo_run.status, repo=repo_run.repo, link=link, commit=repo_run.commit)
        if repo_run.status == "success":
            msg = "✅ Tests passed "
        elif repo_run.status == "failure":
            msg = "❌ Tests failed "
        else:
            msg = "⛔️ Tests errored "
        self.send_msg(
            msg=msg,
            link=link,
            repo=repo_run.repo,
            branch=repo_run.branch,
            commit=repo_run.commit,
            committer=repo_run.committer,
        )

    def xml_parse(self, path, line):
        """Parse the xml file resulted from junit.

        :param path: path to xml file.
        :type path: str
        :param line: command line of the execution to check if it result from pytest as there is a different naming for skip tests between pytest and nosetest.
        :param line: str
        """
        result = dict(summary={}, testcases=[])
        content = xmltodict.parse(self.load_file(path), attr_prefix="", cdata_key="content")["testsuite"]
        result["summary"]["name"] = content["name"]
        if "pytest" in line:
            result_list = ["tests", "errors", "failures", "skipped"]
        else:
            result_list = ["tests", "errors", "failures", "skip"]

        for key in result_list:
            if key == "skipped":
                result["summary"]["skip"] = int(content[key])
            else:
                result["summary"][key] = int(content[key])
        # this check for one test case in xml file
        if not isinstance(content["testcase"], list):
            content["testcase"] = [content["testcase"]]

        status_map = {"error": "errored", "failure": "failed", "skipped": "skipped"}
        for testcase in content["testcase"]:
            obj = dict()
            for key in testcase.keys():
                if key in status_map:
                    obj["status"] = status_map[key]
                    obj["details"] = dict(testcase[key])
                else:
                    obj[key] = testcase[key]

            if not obj.get("status"):
                obj["status"] = "passed"

            result["testcases"].append(obj)
        return result

    def load_file(self, path):
        """Load file content.
        
        :param path: path to file.
        :type path: str
        :return: file content
        :return type: str
        """
        with open(path, "r") as f:
            content = f.read()
        return content

    def install_test_scripts(self, id):
        """Read 0-CI yaml script from the repo home directory and divide it to (prequisties, install, test) scripts.

        :param id: mongo record id to get commit information.
        :type id: str
        :return: prequisties, install, test script.
        """
        repo_run = RepoRun.objects.get(id=id)
        org_repo_name = repo_run.repo.split("/")[0]
        clone = """mkdir -p /opt/code/github/{org_repo_name} &&
        cd /opt/code/github/{org_repo_name} &&
        git clone https://github.com/{repo}.git --branch {branch} &&
        cd /opt/code/github/{repo} &&
        git reset --hard {commit} &&
        """.format(
            repo=repo_run.repo, branch=repo_run.branch, commit=repo_run.commit, org_repo_name=org_repo_name
        ).replace(
            "\n", " "
        )

        script = self.github_get_content(repo=repo_run.repo, ref=repo_run.commit, file_path="zeroCI.yaml")
        if script:
            yaml_script = yaml.load(script)
            prequisties = yaml_script.get("prequisties")
            install = " && ".join(yaml_script.get("install"))
            install_script = clone + install
            test_script = yaml_script.get("script")
            return prequisties, install_script, test_script
        return None, None, None
