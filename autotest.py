from utils import Utils
import os
import sys


class RunTests(Utils):
    def run_tests(self, image_name, run_cmd, timeout=1800):
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
        self.image_check(image_name)
        container_name = self.random_string()
        docker_cmd = "docker run --name {} -t {} /bin/bash -c".format(container_name, image_name)
        cmd = "{} '{} {}'".format(docker_cmd, self.exports, run_cmd)
        response = self.execute_cmd(cmd, timeout=timeout)

        file = "/mnt/log/result/{}.xml".format(self.random_string())
        copy_cmd = "docker cp {}:/test.xml {}".format(container_name, file)
        copy = self.execute_cmd(copy_cmd, timeout=timeout)
        if not copy.returncode:
            file_path = file
        else:
            file_path = None
        remove_container = "docker rm -f {}".format(container_name)
        self.execute_cmd(remove_container, timeout=timeout)
        return response, file_path

    def image_check(self, image_name):
        """Check if the docker image exist before run tests.

        :param image_name: docker image name 
        :type image_name: str
        """
        if image_name == "{}/jumpscalex".format(self.username):
            response = self.execute_cmd('docker images | tail -n+2 | awk "{print \$1}"')
            images_name = response.stdout.split()
            if image_name not in images_name:
                self.send_msg("Could not find image")
                sys.exit()
