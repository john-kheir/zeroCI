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
        home_user = os.path.expanduser('~')
        if os.path.exists('{}/.ssh/id_rsa.pub'.format(home_user)):
            with open('{}/.ssh/id_rsa.pub'.format(home_user), 'r') as file:
                ssh = file.readline().replace('\n', '')
        else:              
            cmd = 'ssh-keygen -t rsa -N "" -f {}/.ssh/id_rsa -q -P ""; ssh-add {}/.ssh/id_rsa'.format(home_user, home_user)
            self.execute_cmd(cmd)
            ssh = self.load_ssh_key()
        return ssh


    def execute_command(self, cmd, ip='', port=22):
        target = "ssh -o 'StrictHostKeyChecking no' -p {} root@{} '{}'".format(port, ip, cmd)
        response = self.execute_cmd(target)
        return response
    
    def deploy_vm(self):
        jwt = "eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhenAiOiI5WGstV3NuaGs4NERxRHY3RTUyWlpqMFBpOGM5IiwiZXhwIjoxNTYzMTg4MjQ2LCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJyZWZyZXNoX3Rva2VuIjoiMWhHeGpiRVBKUGllellkYlR6UjNyWEI4cnVTaCIsInNjb3BlIjpbInVzZXI6bWVtYmVyb2Y6dGhyZWVmb2xkLnN5c2FkbWluIl0sInVzZXJuYW1lIjoibWlraGFpZWIifQ.xm0U-JEONCXSK_NhR7EAlwv9HRDxroq8SLHB4hEN3Haothpe_gmScHXcuGoofbLhWtIg6z629oC3lBhz9MUjbLQZaO-2O8ADmAxtVj6Jl18hKo22GXVM42nusce9HlUF"
        # create vm ubuntu 18.04
        ens4 = """network:
  version: 2
  renderer: networkd
  ethernets:
    ens4:
      dhcp4: true
      dhcp6: true
        """
        ssh_key = self.load_ssh_key()
        flist = 'https://hub.grid.tf/tf-bootable/ubuntu:18.04.flist'
        vm_name = self.random_string()
        vm_uuid = None
        for _ in range(6):
            node_ip = self.get_node()
            print(node_ip)
            client_name = self.random_string()
            self.node = j.clients.zos.get(client_name, host=node_ip, password=jwt)
            port = random.randint(22000, 25000)
            ports = {port: 22}
            try:
                vm_uuid = self.node.client.kvm.create(name=vm_name, flist=flist, port=ports, memory=4096,cpu=4, nics=[{'type':'default'}],
                        config= {'/root/.ssh/authorized_keys': ssh_key, '/etc/netplan/ens4.yaml': ens4})
                break
            except Exception:
                time.sleep(10)
                

        time.sleep(60)
        if vm_uuid:
            return vm_uuid, node_ip, port
        return None, None, None

    
    def install_app(self, node_ip, port, id):
        repo_run = RepoRun.objects.get(id=id)
        copy_cmd = 'scp -P {port} -o StrictHostKeyChecking=no install.sh root@{node_ip}:/install.sh'.format(port=port, node_ip=node_ip)
        response = self.execute_cmd(copy_cmd)
        if not response.returncode:
            print("file is sent")
            install_cmd = "export branch={branch}; export commit={commit}; bash /install.sh".format(branch=repo_run.branch, commit=repo_run.commit)
            response_2 = self.execute_command(cmd=install_cmd, ip=node_ip, port=port)
            if response_2.returncode:
                repo_run.status = "error"
                repo_run.result.append({"type": "log", "status": "error", "content": response_2.stderr})
                repo_run.save()
                self.report(id=id)
                print("finish installation")
            else:
                return True
        else:
            repo_run.status = "error"
            repo_run.result.append({"type": "log", "status": "error", "content": response.stderr})
            repo_run.save()
            self.report(id=id)
        return False
    
    def run_test(self, run_cmd, node_ip, port):
        envs = ""
        for env in self.environment.keys():
            envs = envs + "export {}={}; ".format(env, self.environment[env])
        cmd = envs + run_cmd
        print("start running tests")
        response = self.execute_command(cmd, ip=node_ip, port=port)
        print("finish tests")
        file_path = "/mnt/log/result/{}.xml".format(self.random_string())
        # copy_cmd = 'scp -P {port} root@{node_ip}:/test.xml {file_name}'.format(port=port, file_name=file_path, node_ip=node_ip)
        # response_2 = self.execute_command(cmd=copy_cmd, ip=node_ip, port=port)
        # if response_2.returncode:
        file_path = False 
        return response.returncode, response.stderr, file_path

    def destroy_vm(self, uuid):
        print("remove")
        if self.node:
            self.node.client.kvm.destroy(uuid)
            print("remove done")

        
        