FROM ubuntu:latest

ARG BRANCH=main

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
 && apt-get install -y git python3 python3-venv

RUN echo "cloning ${BRANCH}"
RUN git clone --branch ${BRANCH} https://github.com/martomi/chiadog.git \
 && cd chiadog \
 && /usr/bin/sh ./install.sh

WORKDIR /chiadog
ENTRYPOINT ["bash", "./start.sh"]
