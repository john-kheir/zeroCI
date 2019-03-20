FROM ubuntu:18.04

ARG branch
ARG commit
RUN apt-get update; apt-get install -y python3.6 curl git locales language-pack-en
