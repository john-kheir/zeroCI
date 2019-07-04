import json
import os

if not os.path.exists("status.txt"):
    with open("status.txt", "w") as f:
        data = {"test": "dummy"}
        json.dump(data, f)

with open("status.txt", "r") as f:
    data = json.load(f)
data["builders"] = "failure"
data["builders_log"] = "http://188.165.233.148:6010/2019-05-29_builders.log"
data["build"] = "success"
data["build_log"] = "http://188.165.233.148:6010/b1b16a2.log"
data["tests"] = "success"
data["tests_log"] = "http://188.165.233.148:6010/b1b16a2.log"
data["black"] = "failure"
data["black_log"] = "http://188.165.233.148:6010/b1b16a2_format.log"


with open("status.txt", "w") as f:
    json.dump(data, f)
