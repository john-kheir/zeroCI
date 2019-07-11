from actions import Actions
from utils import Utils
import os
from datetime import datetime
from db import ProjectRun


actions = Actions()


def builders():
    image_name = "builders"
    project = ProjectRun(timestamp=datetime.now().timestamp(), name="Builders")
    project.save()
    line = "apt-get update; source /sandbox/env.sh; kosmos --instruct /sandbox/code/github/threefoldtech/test.toml;\
         cd /sandbox/code/github/threefoldtech/jumpscaleX/ ;git pull; nosetests-3.4 -v --with-xunit --xunit-file=/test.xml\
        --xunit-testsuite-name=Builders Jumpscale/builder/test/ --tc-file=Jumpscale/builder/test/flist/config.ini\
        --tc=itsyou.username:$IYO_USERNAME --tc=itsyou.client_id:$IYO_CLIENT_ID --tc=itsyou.client_secret:$IYO_CLIENT_SECRET\
        --tc=zos_node.node_ip:$ZOS_NODE_IP --tc=zos_node.node_jwt:$JWT"
    response, stdout, file_path = actions.container_run(image_name=image_name, run_cmd=line, timeout=13000)
    status = "success"
    if file_path:
        if response:
            status = "failure"
        result = actions.xml_parse(path=file_path, line=line)
        project.result.append(
            {"type": "testsuite", "status": status, "name": result["summary"]["name"], "content": result}
        )
    else:
        if response:
            status = "failure"
        project.result.append({"type": "log", "status": status, "name": "Builders", "content": stdout})

    project.status = status
    project.save()
    if status == "success":
        actions.send_msg("Builders tests passed {}".format(actions.serverip))
    else:
        actions.send_msg("Builders tests failed {}".format(actions.serverip))
