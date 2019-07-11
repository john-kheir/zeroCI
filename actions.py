from utils import Utils
from db import *
from docker_container import Docker


class Actions(Utils):
    def container_run(self, image_name, run_cmd, timeout=1800):
        """Run tests with specific image and commit.

        :param image_name: docker image name.
        :type image_name: str
        :param run_cmd: command line that will be run tests. 
        :type run_cmd: str
        :param repo: full repo name
        :type repo: str
        :param commit: commit hash 
        :type commit: str
        """
        container_name = self.random_string()
        docker = Docker()
        result, stdout = docker.run(
            image_name=image_name, name=container_name, command=run_cmd, environment=self.environment, timeout=timeout
        )
        xml_path = docker.copy_from(name=container_name, source_path="/test.xml", target_path="/mnt/log/result")
        docker.remove_container(container_name)
        return result, stdout, xml_path

    def test_run(self, image_name, id):
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
        status = "success"
        content = self.github_get_content(repo=repo_run.repo, ref=repo_run.commit)
        if content:
            lines = content.splitlines()
            for i, line in enumerate(lines):
                status = "success"
                if line.startswith("#"):
                    continue
                response, stdout, file_path = self.container_run(image_name=image_name, run_cmd=line)
                if file_path:
                    if response:
                        status = "failure"
                    result = self.xml_parse(path=file_path, line=line)
                    repo_run.result.append(
                        {"type": "testsuite", "status": status, "name": result["summary"]["name"], "content": result}
                    )
                else:
                    if response:
                        status = "failure"
                        name = "cmd {}".format(i + 1)
                    repo_run.result.append({"type": "log", "status": status, "name": name, "content": stdout})
        else:

            repo_run.result.append({"type": "log", "status": status, "name": "No tests", "content": "No tests found"})
        repo_run.save()

    def test_black(self, image_name, id):
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
        link = self.serverip
        status = "success"
        line = "black {} -l 120 -t py37 --exclude 'templates'".format(self.project_path)
        response, stdout, file = self.container_run(image_name=image_name, run_cmd=line)
        if "reformatted" in stdout:
            status = "failure"
        repo_run.result.append({"type": "log", "status": status, "name": "Black Formatting", "content": stdout})
        repo_run.save()
        self.github_status_send(
            status=status, link=link, repo=repo_run.repo, commit=repo_run.commit, context="Black-Formatting"
        )

    def build_image(self, branch, commit, id):
        """Build a docker image to install application.

        :param branch: branch name.
        :type branch: str
        :param commit: commit hash.
        :type commit: str
        :param committer: name of the committer on github.
        :type committer: str
        """
        docker = Docker()
        image_name = self.random_string()
        build_args = {"branch": branch, "commit": commit}
        response = docker.build(image_name=image_name, timeout=1800, docker_file="Dockerfile", build_args=build_args)
        if response:
            docker.remove_failure_images()
            repo_run = RepoRun.objects(id=id).first()
            repo_run.status = "error"
            repo_run.result.append({"type": "log", "status": "error", "content": response})
            repo_run.save()
            self.report(id=id)
            return False
        return image_name

    def cal_status(self, id):
        repo_run = RepoRun.objects.get(id=id)
        status = "success"
        for result in repo_run.result:
            if result["status"] != "success":
                status = result["status"]
        repo_run.status = status
        repo_run.save()

    def build_and_test(self, id):
        repo_run = RepoRun.objects.get(id=id)
        image_name = self.build_image(branch=repo_run.branch, commit=repo_run.commit, id=id)
        if image_name:
            self.test_black(image_name=image_name, id=id)
            self.test_run(image_name=image_name, id=id)
            self.cal_status(id=id)
            self.report(id=id)
            docker = Docker()
            docker.remove_image(image_name)
