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
        self.docker_client.api.create_container(image=image_name, name=name, command=command, environment=environment)

    def start(self, name):
        self.docker_client.api.start(name)

    def wait(self, name, timeout):
        try:
            result = self.docker_client.api.wait(name, timeout=timeout)
            return result["StatusCode"]
        except Exception as e:
            return e.args

    def remove_container(self, name):
        self.docker_client.api.remove_container(name, force=True)

    def logs(self, name):
        log = self.docker_client.api.logs(name, stdout=True, stderr=True)
        return log

    def copy_from(self, name, source_path, target_path):
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

        file_name = target_path.split("/")[-1]
        tar_file.extract(file_name, path=output_dir)
        os.remove(tarfile_name)
        xml_file_path = os.path.join(output_dir, file_name)

        return xml_file_path

    def build(self, image_name, timeout, docker_file, build_args, path="."):
        try:
            self.docker_client.images.build(
                path=path, tag=image_name, dockerfile=docker_file, timeout=timeout, forcerm=True, buildargs=build_args
            )
            return 0
        except Exception as e:
            return e.args

    def run(self, image_name, name, command, environment, timeout):
        self.create(image_name=image_name, name=name, command=command, environment=environment)
        self.start(name=name)
        result = self.wait(name=name, timeout=timeout)
        stdout = self.logs(name=name)
        return result, stdout

    def remove_image(self, name_or_id):
        self.docker_client.images.remove(name_or_id, force=True)

    def remove_failure_images(self):
        images = self.docker_client.images.list()
        for image in images:
            if image.tags == []:
                id = image.id.split(":")[-1]
                try:
                    self.docker_client.images.remove(id)
                except Exception as e:
                    return e.args
