FROM ubuntu:18.04

ARG branch
ARG commit
RUN apt-get update; apt-get install -y python3.6 curl git locales language-pack-en rsync unzip
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
RUN mkdir -p /sandbox/code/github/threefoldtech
RUN cd /sandbox/code/github/threefoldtech; git clone --branch $branch https://github.com/threefoldtech/jumpscaleX.git
RUN cd /sandbox/code/github/threefoldtech/jumpscaleX/; git reset --hard $commit

RUN python3.6 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py -1 -y -w -p
RUN /bin/bash -c "source /sandbox/env.sh; js_shell 'j.builders.db.zdb.install()'"
RUN pip3 install pytest nose nose-progressive nose-testconfig pytest-testconfig requests>=2.11.1 parameterized black loguru
RUN pip3 install git+https://github.com/AhmedHanafy725/junit2html_plugin
RUN pip3 install -e 'git+https://github.com/threefoldtech/0-hub#egg=zerohub&subdirectory=client'
COPY ./test.toml /sandbox/code/github/threefoldtech/
COPY ./black.py /sandbox/code/github/threefoldtech/jumpscaleX/scripts
RUN cd /sandbox/code/github/threefoldtech/jumpscaleX; git checkout Jumpscale/jumpscale_generated.py
