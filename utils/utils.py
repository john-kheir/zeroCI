from subprocess import PIPE, Popen, TimeoutExpired, CompletedProcess
from uuid import uuid4
import time
import os
import re
import codecs

import xmltodict

from .config import Configs

ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


class Utils(Configs):
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
