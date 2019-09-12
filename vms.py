from utils import Utils
from Jumpscale import j
from urllib.parse import urlparse
import random
import os
import time
from db import *
import paramiko


RETRIES = 5


class Complete_Executuion:
    returncode = None
    stdout = None
    stderr = None

    def __init__(self, rc, out, err):
        self.returncode = rc
        self.stdout = out
        self.stderr = err


class VMS(Utils):
    def __init__(self):
        super().__init__()
        self.node = None

    def list_nodes(self):
        """List farm nodes.

        :return: list of farm ips
        :return type: list
        """
        ips = []
        try:
            farm = j.sal_zos.farm.get("freefarm")
            nodes = farm.filter_online_nodes()
            for node in nodes:
                url = node["robot_address"]
                ip = urlparse(url).hostname
                ips.append(ip)
        except:
            ips = [
                "10.102.178.130",
                "10.102.191.143",
                "10.102.117.236",
                "10.102.104.231",
                "10.102.234.229",
                "10.102.71.171",
                "10.102.96.237",
                "10.102.167.219",
                "10.102.141.236",
                "10.102.113.188",
                "10.102.186.165",
                "10.102.64.213",
                "10.102.189.153",
                "10.102.227.115",
                "10.102.115.21",
                "10.102.57.140",
            ]
        return ips

    def get_node(self):
        """Get node ip from farm randomly.

        :return: node ip
        :return type: str
        """
        # should pick with a rule
        nodes = self.list_nodes()
        node = random.choice(nodes)
        return node

    def load_ssh_key(self):
        """Load sshkey if it is exist or genertate one if not.

        :return: public key
        :return type: str
        """
        home_user = os.path.expanduser("~")
        if os.path.exists("{}/.ssh/id_rsa.pub".format(home_user)):
            with open("{}/.ssh/id_rsa.pub".format(home_user), "r") as file:
                ssh = file.readline().replace("\n", "")
        else:
            cmd = 'ssh-keygen -t rsa -N "" -f {}/.ssh/id_rsa -q -P ""; ssh-add {}/.ssh/id_rsa'.format(
                home_user, home_user
            )
            self.execute_cmd(cmd)
            ssh = self.load_ssh_key()
        return ssh

    def execute_command(self, cmd, ip="", port=22, timeout=7200, environment={}):
        """Execute a command on a remote machine using ssh.

        :param cmd: command to be executed on a remote machine.
        :type cmd: str
        :param ip: machine's ip.
        :type ip: str
        :param port: machine's ssh port.
        :type port: int
        :param timout: stop execution after a certain time.
        :type timeout: int
        :return: subprocess object containing (returncode, stdout, stderr)
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
        client.connect(hostname=ip, port=port, timeout=30)
        _, stdout, stderr = client.exec_command(cmd, timeout=timeout, environment=environment)
        try:
            out = stdout.read().decode()
            err = stderr.read().decode()
            rc = stdout.channel.recv_exit_status()
        except:
            stdout.channel.close()
            err = "Error Timeout Exceeded {}".format(timeout)
            out = ""
            rc = 124
        return Complete_Executuion(rc, out, err)

    def get_remote_file(self, ip, port, remote_path, local_path):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
        client.connect(hostname=ip, port=port, timeout=30)
        ftp = client.open_sftp()
        try:
            ftp.get(remote_path, local_path)
            return True
        except:
            return False

    def prepare(self, prequisties):
        """Prepare the machine's parameters before creating it depend on the prequisties needed.

        :param prequisties: list of prequisties needed.
        :type prequisties: list
        """
        if "docker" in prequisties:
            self.flist = "https://hub.grid.tf/qa_tft_1/ubuntu18.04_docker.flist"
            self.disk_path = "/var/cache/{}.qcow2".format(self.random_string())
            self.node.client.bash("qemu-img create -f qcow2 {} 30G".format(self.disk_path)).get()
            self.media.append({"url": self.disk_path})

    def deploy_vm(self, prequisties=""):
        """Deploy a virtual machine on zos node.

        :param prequisties: list of prequisties needed.
        :type prequisties: list
        :return: node info (uuid, ip, port) required to access the virtual machine created.
        """
        iyo_name = self.random_string()
        iyo = j.clients.itsyouonline.get(
            iyo_name, baseurl="https://itsyou.online/api", application_id=self.iyo_id, secret=self.iyo_secret
        )
        self.jwt = iyo.jwt_get(scope="user:memberof:threefold.sysadmin").jwt
        self.ssh_key = self.load_ssh_key()
        self.cpu = 2
        self.memory = 2048
        self.media = []
        self.flist = "https://hub.grid.tf/qa_tft_1/ubuntu:18.04.flist"
        for _ in range(RETRIES):
            self.vm_name = self.random_string()
            self.node_ip = self.get_node()
            self.client_name = self.random_string()
            self.node = j.clients.zos.get(self.client_name, host=self.node_ip, password=self.jwt)
            self.port = random.randint(22000, 25000)
            self.ports = {self.port: 22}
            try:
                self.prepare(prequisties=prequisties)
                self.vm_uuid = self.node.client.kvm.create(
                    name=self.vm_name,
                    flist=self.flist,
                    port=self.ports,
                    memory=self.memory,
                    cpu=self.cpu,
                    nics=[{"type": "default"}],
                    config={"/root/.ssh/authorized_keys": self.ssh_key},
                    media=self.media,
                )
                break
            except:
                time.sleep(1)
                self.vm_uuid = None

        time.sleep(40)
        if self.vm_uuid:
            return self.vm_uuid, self.node_ip, self.port
        return None, None, None

    def install_app(self, node_ip, port, install_script):
        """Install application to be tested.

        :param node_ip: mahcine's ip
        :type node_ip: str
        :param port: machine's ssh port
        :type port: int
        :param install_script: bash script to install script
        :type install_script: str
        """
        prepare_script = self.prepare_script()
        script = prepare_script + install_script
        response = self.execute_command(cmd=script, ip=node_ip, port=port, environment=self.environment)
        return response

    def run_test(self, run_cmd, node_ip, port, timeout):
        """Run test command and get the result as xml file if the running command is following junit otherwise result will be log.

        :param run_cmd: test command to be run.
        :type run_cmd: str
        :param node_ip: machine's ip
        :type node_ip: str
        :param port: machine's ssh port
        :type port: int
        :param timout: stop execution after a certain time.
        :type timeout: int
        :return: path to xml file if exist and subprocess object containing (returncode, stdout, stderr)
        """
        response = self.execute_command(run_cmd, ip=node_ip, port=port, timeout=timeout, environment=self.environment)
        file_path = "{}/{}.xml".format(self.result_path, self.random_string())
        remote_path = "/test.xml"
        copied = self.get_remote_file(ip=node_ip, port=port, remote_path=remote_path, local_path=file_path)
        if copied:
            file_path = file_path
        else:
            file_path = None
        return response, file_path

    def destroy_vm(self, uuid):
        """Destory the virtual machine after finishing test.
        
        :param uuid: machine's uuid.
        :type uuid: str
        """
        if self.node:
            self.node.client.kvm.destroy(uuid)
        if self.media:
            self.node.client.bash("rm -rf {}".format(self.disk_path)).get()

    def prepare_script(self):
        return """apt-get update &&
        export DEBIAN_FRONTEND=noninteractive &&
        apt-get install -y git python3.6 python3-pip software-properties-common &&
        apt-get install -y --reinstall python3-apt &&
        pip3 install black &&
        """
