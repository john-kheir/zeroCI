from utils import Utils
from Jumpscale import j
from urllib.parse import urlparse
import random
import os
import time
from db import *


class VMS(Utils):
    def __init__(self):
        super().__init__()
        self.node = None

    def list_nodes(self):
        farm = j.sal_zos.farm.get("freefarm")
        nodes = farm.list_nodes()
        ips = []
        for node in nodes:
            url = node["robot_address"]
            ip = urlparse(url).hostname
            ips.append(ip)
        return ips

    def get_node(self):
        # should pick with a rule
        nodes = self.list_nodes()
        node = random.choice(nodes)
        return node

    def load_ssh_key(self):
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

    def execute_command(self, cmd, ip="", port=22, timeout=3600):
        target = "ssh -o 'StrictHostKeyChecking no' -p {} root@{} '{}'".format(port, ip, cmd)
        response = self.execute_cmd(target, timeout=timeout)
        return response

    def prepare(self, prequisties):
        if prequisties == "docker":
            self.flist = "https://hub.grid.tf/qa_tft_1/ubuntu18.04_docker_latest.flist"

    def deploy_vm(self, prequisties=""):
        iyo_name = self.random_string()
        iyo = j.clients.itsyouonline.get(
            iyo_name, baseurl="https://itsyou.online/api", application_id=self.iyo_id, secret=self.iyo_secret
        )
        self.jwt = iyo.jwt_get(scope="user:memberof:threefold.sysadmin").jwt
        self.ens4 = """network:
  version: 2
  renderer: networkd
  ethernets:
    ens4:
      dhcp4: true
      dhcp6: true
        """
        self.ssh_key = self.load_ssh_key()
        self.cpu = 2
        self.memory = 2048
        self.media = []
        self.flist = "https://hub.grid.tf/tf-bootable/ubuntu:18.04.flist"
        self.vm_name = self.random_string()
        self.node_ip = "10.102.18.170" #self.get_node()
        self.client_name = self.random_string()
        self.node = j.clients.zos.get(self.client_name, host=self.node_ip, password=self.jwt)
        self.port = random.randint(22000, 25000)
        self.ports = {self.port: 22}
        self.prepare(prequisties=prequisties)
        self.vm_uuid = self.node.client.kvm.create(
            name=self.vm_name,
            flist=self.flist,
            port=self.ports,
            memory=self.memory,
            cpu=self.cpu,
            nics=[{"type": "default"}],
            config={"/root/.ssh/authorized_keys": self.ssh_key, "/etc/netplan/ens4.yaml": self.ens4},
            media=self.media,
        )

        time.sleep(40)
        if self.vm_uuid:
            return self.vm_uuid, self.node_ip, self.port
        return None, None, None

    def install_app(self, node_ip, port, install_script):
        response = self.execute_command(cmd=install_script, ip=node_ip, port=port)
        return response

    def run_test(self, run_cmd, node_ip, port, timeout):
        envs = ""
        for env in self.environment.keys():
            envs = envs + "export {}={}; ".format(env, self.environment[env])
        cmd = envs + run_cmd
        response = self.execute_command(cmd, ip=node_ip, port=port, timeout=timeout)
        file_path = "{}/{}.xml".format(self.result_path, self.random_string())
        copy_cmd = 'scp -P {port} -o "StrictHostKeyChecking no" root@{node_ip}:/test.xml {file_name}'.format(
            port=port, file_name=file_path, node_ip=node_ip
        )
        response_2 = self.execute_cmd(cmd=copy_cmd, timeout=30)
        if response_2.returncode:
            file_path = None
        return response, file_path

    def destroy_vm(self, uuid):
        if self.node:
            self.node.client.kvm.destroy(uuid)
