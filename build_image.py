from utils import Utils
from datetime import datetime
import sys
import os


class BuildImage(Utils):

    def image_bulid(self, image_name, branch, commit=''):
        """Build docker image with specific branch and commit.

        :param image_name: docker image name.
        :type image_name: str
        :param branch: branch name.
        :type branch: str
        :param commit: commit hash (default='' for last commit).
        :type commit: str
        """
        cmd = 'docker build --force-rm -t {} . --build-arg branch={} --build-arg commit={}'.format(image_name, branch, commit)
        response = self.execute_cmd(cmd)
        return response

    def images_clean(self, image_name=None):
        """Clean docker images.

        :param image_name: docker image name (default=None to clean all incomplete images).
        :type image_name: str
        """
        if image_name:
            response = self.execute_cmd('docker rmi -f {}'.format(image_name))
        response = self.execute_cmd('docker images | tail -n+2 | awk "{print \$1}"')
        images_name = response.stdout.split()
        response = self.execute_cmd('docker images | tail -n+2 | awk "{print \$3}"')
        images_id = response.stdout.split()
        for i in range(0, len(images_id)):
            if images_name[i] == '<none>':
                response = self.execute_cmd('docker rmi -f {}'.format(images_id[i]))
