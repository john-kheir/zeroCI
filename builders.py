from autotest import RunTests
from build_image import BuildImage
from utils import Utils
import os
from datetime import datetime


utils = Utils()
test = RunTests()
image_name = "builders"
repo = utils.repo[0]
file_name = "{}_builders".format(str(datetime.now())[:8] + str(datetime.now().day + 1))
html_path = "/{}.html".format(file_name)
line = "apt-get update; cd /sandbox/code/github/threefoldtech/jumpscaleX/ ;git pull;\
        nosetests-3.4 -v --with-html --html-testsuite-name=Builders --html-file={} Jumpscale/builder/test/ \
        --tc-file=Jumpscale/builder/test/flist/config.ini --tc=itsyou.username:$IYO_USERNAME --tc=itsyou.client_id:$IYO_CLIENT_ID \
        --tc=itsyou.client_secret:$IYO_CLIENT_SECRET --tc=zos_node.node_ip:$ZOS_NODE_IP --tc=zos_node.node_jwt:$JWT".format(
    html_path
)
response, copy = test.run_tests(
    image_name=image_name, run_cmd=line, repo=repo, commit="", html_path=html_path, timeout=13000
)
test.write_file(text="---> {}".format(line), file_name="{}.log".format(file_name))
test.write_file(text=response.stdout, file_name="{}.log".format(file_name))
if not copy:
    file_name = "{}.html".format(file_name)
else:
    file_name = "{}.log".format(file_name)
file_link = "{}/{}".format(utils.serverip, file_name)
if response.returncode:
    utils.send_msg("Builders tests failed {}".format(file_link))
    status = "failure"
else:
    utils.send_msg("Builders tests passed {}".format(file_link))
    status = "success"

utils.update_json_file(path="/mnt/log/status.json", param=file_name, value=status)
utils.update_json_file(param="builders", value=status)
utils.update_json_file(param="builders_log", value=file_link)
