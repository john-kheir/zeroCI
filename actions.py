from utils import Utils
from db import *
import os
from vms import VMS
from datetime import datetime

vms = VMS()


class Actions(Utils):
    def test_run(self, node_ip, port, id, test_script, db_run, timeout):
        """Runs tests with specific commit and store the result in DB.
        
        :param image_name: docker image tag.
        :type image_name: str
        :param id: DB id of this commit details.
        :type id: str
        """
        repo_run = db_run.objects.get(id=id)
        status = "success"
        if test_script:
            for i, line in enumerate(test_script):
                status = "success"
                if line.startswith("#"):
                    continue
                response, stdout, file_path = vms.run_test(run_cmd=line, node_ip=node_ip, port=port, timeout=timeout)
                if file_path:
                    if response:
                        status = "failure"
                    try:
                        result = self.xml_parse(path=file_path, line=line)
                        repo_run.result.append(
                            {
                                "type": "testsuite",
                                "status": status,
                                "name": result["summary"]["name"],
                                "content": result,
                            }
                        )
                    except:
                        name = "cmd {}".format(i + 1)
                        repo_run.result.append({"type": "log", "status": status, "name": name, "content": stdout})
                    os.remove(file_path)
                else:
                    if response:
                        status = "failure"
                    name = "cmd {}".format(i + 1)
                    repo_run.result.append({"type": "log", "status": status, "name": name, "content": stdout})
        else:

            repo_run.result.append({"type": "log", "status": status, "name": "No tests", "content": "No tests found"})
        repo_run.save()

    def test_black(self, node_ip, port, id, db_run, timeout):
        """Runs black formatting test on the repo with specific commit.

        :param image_name: docker image tag.
        :type image_name: str
        :param id: DB id of this commit details.
        :type id: str
        """
        repo_run = db_run.objects.get(id=id)
        link = self.serverip
        status = "success"
        line = "black /opt/code/github/{} -l 120 -t py37 --exclude 'templates'".format(repo_run.repo)
        response, stdout, file = vms.run_test(run_cmd=line, node_ip=node_ip, port=port, timeout=timeout)
        if "reformatted" in stdout:
            status = "failure"
        repo_run.result.append({"type": "log", "status": status, "name": "Black Formatting", "content": stdout})
        repo_run.save()
        self.github_status_send(
            status=status, link=link, repo=repo_run.repo, commit=repo_run.commit, context="Black-Formatting"
        )

    def build(self, install_script, id, db_run, prequisties=""):
        if install_script:
            uuid, node_ip, port = vms.deploy_vm(prequisties=prequisties)
            if uuid:
                response = vms.install_app(node_ip=node_ip, port=port, install_script=install_script)
                if response.returncode:
                    repo_run = db_run.objects.get(id=id)
                    repo_run.result.append({"type": "log", "status": "error", "content": response.stderr})
                    self.cal_status(id=id, db_run=db_run)
                    repo_run.save()
                return uuid, response, node_ip, port

            else:
                repo_run = db_run.objects.get(id=id)
                repo_run.result.append({"type": "log", "status": "error", "content": "Couldn't deploy a vm"})
                repo_run.save()
                self.cal_status(id=id, db_run=db_run)           
        else:
            repo_run = db_run.objects.get(id=id)
            repo_run.result.append({"type": "log", "status": "success", "content": "Didn't find something to install"})
            repo_run.save()
            self.cal_status(id=id, db_run=db_run)

        return None, None, None, None

    def cal_status(self, id, db_run):
        """Calculates the status of whole tests ran on the BD's id.
        
        :param id: DB id of this commit details.
        :type id: str
        """
        repo_run = db_run.objects.get(id=id)
        status = "success"
        for result in repo_run.result:
            if result["status"] != "success":
                status = result["status"]
        repo_run.status = status
        repo_run.save()

    def build_and_test(self, id):
        """Builds, runs tests, calculates status and gives report on telegram and github.
        
        :param id: DB id of this commit details.
        :type id: str
        """
        prequisties, install_script, test_script = self.install_test_scripts(id=id)
        uuid, response, node_ip, port = self.build(install_script=install_script, id=id, db_run=RepoRun, prequisties=prequisties)
        if uuid:
            if not response.returncode:
                self.test_black(node_ip=node_ip, port=port, id=id, db_run=RepoRun, timeout=500)
                self.test_run(node_ip=node_ip, port=port, id=id, test_script=test_script, db_run=RepoRun, timeout=3600)
                self.cal_status(id=id, db_run=RepoRun)
            vms.destroy_vm(uuid)
        self.report(id=id)

    def run_project(self, project_name, install_script, test_script, prequisties, timeout):
        status = "pending"
        project_run = ProjectRun(timestamp=datetime.now().timestamp(), status=status, name=project_name)
        project_run.save()
        id = str(project_run.id)
        uuid, response, node_ip, port = self.build(install_script=install_script, id=id, db_run=ProjectRun, prequisties=prequisties)
        if uuid:
            if not response.returncode:
                self.test_run(node_ip=node_ip, port=port, id=id, test_script=test_script, db_run=ProjectRun, timeout=timeout)
                self.cal_status(id=id, db_run=ProjectRun)
                project_run = ProjectRun.objects.get(id=id)

            vms.destroy_vm(uuid)

        if project_run.status == "success":
            self.send_msg("✅ {} tests passed {}".format(project_name, self.serverip))
        elif project_run.status == "failure":
            self.send_msg("❌ {} tests failed {}".format(project_name, self.serverip))
        else:
            self.send_msg("⛔️ {} tests errored {}".format(project_name, self.serverip))
