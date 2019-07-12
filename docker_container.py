import docker
import tarfile
import shutil
import os
from utils import Utils

utils = Utils()


class Docker:
    def __init__(self):
        self.docker_client = docker.from_env()

    def create(self, image_name, name, command, environment):
        """Create docker container without start it.

        :param image_name: docker image tag.
        :type image_name: str
        :param name: docker container name.
        :type name: str
        :param command: docker container startup command.
        :type command: str
        :param environment: docker container environmnet variables.
        :type environment: dict(ex: {"key": value} or list (ex: ["key=value"])
        """
        self.docker_client.api.create_container(image=image_name, name=name, command=command, environment=environment)

    def start(self, name):
        """Start docker container.

        :param name: docker container name.
        :type name: str
        """
        self.docker_client.api.start(name)

    def wait(self, name, timeout):
        """Wait docker container to finish startup command.

        :param name: docker container name.
        :type name: str
        :param timeout: docker container timeout.
        :type timeout: int
        """
        try:
            result = self.docker_client.api.wait(name, timeout=timeout)
            return result["StatusCode"]
        except Exception as e:
            return e.args

    def remove_container(self, name):
        """Remove docker container.

        :param name: docker container name.
        :type name: str
        """
        self.docker_client.api.remove_container(name, force=True)

    def logs(self, name):
        """Get docker container logs.

        :param name: docker container name.
        :type name: str
        :return: logs in string format.
        :return type: str
        """
        log = self.docker_client.api.logs(name, stdout=True, stderr=True)
        return log.decode()

    def copy_from(self, name, source_path, target_path):
        """Copy docker container files or dirs.

        :param name: docker container name.
        :type name: str
        :param source_path: path of file or dir in docker.
        :type source_path: str
        :param target_path: path of parent dir should contains output files.
        :type target_path: str
        :return: xml file path.
        :return type: str
        """
        try:
            bits, status = self.docker_client.api.get_archive(container=name, path=source_path)
        except:
            return False
        tarfile_name = utils.random_string()
        with open(tarfile_name, "wb") as f:
            for chunk in bits:
                f.write(chunk)

        tar_file = tarfile.open(tarfile_name)
        output_dir = os.path.join(target_path, utils.random_string())

        file_name = source_path.split("/")[-1]
        tar_file.extract(file_name, path=output_dir)
        os.remove(tarfile_name)
        xml_file_path = os.path.join(output_dir, file_name)

        return xml_file_path

    def build(self, image_name, timeout, docker_file, build_args, path="."):
        """Build docker image using dockerfile.

        :param image_name: docker image tag.
        :type name: str
        :param timeout: timeout for build the image.
        :type timeout: int
        :param docker_file: dockerfile name.
        :type docker_file: str
        :param build_args: args used in build like env vars.
        :type build_args: dict
        :param path: path for directory that contains dockerfile.
        :type path: str
        :return: 0 in case of success, error msg in case of failure. 
        """
        try:
            self.docker_client.images.build(
                path=path, tag=image_name, dockerfile=docker_file, timeout=timeout, forcerm=True, buildargs=build_args
            )
            return 0
        except Exception as e:
            return e.args

    def run(self, image_name, name, command, environment, timeout):
        """Run docker container.

        :param image_name: docker image tag.
        :type name: str
        :param name: docker container name.
        :type name: str
        :param command: docker container startup command.
        :type command: str
        :param environment: docker container environmnet variables.
        :type environment: dict(ex: {"key": value} or list (ex: ["key=value"])
        :param timeout: docker container timeout.
        :type timeout: int
        :return result: 0 in case of success, error msg in case of failure.
        :return stdout: logs of container startup command.
        """
        self.create(image_name=image_name, name=name, command=command, environment=environment)
        self.start(name=name)
        result = self.wait(name=name, timeout=timeout)
        stdout = self.logs(name=name)
        return result, stdout

    def remove_image(self, name_or_id):
        """Force remove docker image.

        :param name_or_id: docker image name or id.
        :type name_or_id: str
        """
        self.docker_client.images.remove(name_or_id, force=True)

    def remove_failure_images(self):
        """Remove docker image that doesn't have tag.

        :return: error message in case of failure.
        """
        images = self.docker_client.images.list()
        for image in images:
            if image.tags == []:
                id = image.id.split(":")[-1]
                try:
                    self.docker_client.images.remove(id)
                except Exception as e:
                    return e.args
