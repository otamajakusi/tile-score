# syntax = docker/dockerfile:experimental
FROM ubuntu:18.04

RUN apt update
RUN apt install -y git vim npm wget python3.7 curl
RUN npm i -g npm@latest
RUN npm -v
RUN npm i -g n
RUN n stable
RUN node -v
RUN mkdir -m 700 $HOME/.ssh
RUN ssh-keyscan github.com > $HOME/.ssh/known_hosts
RUN --mount=type=ssh git clone git@github.com:otamajakusi/tile-score
WORKDIR /tile-score/server
COPY env.yml /tile-score/env
RUN npm i
RUN apt install -y python3-pip
RUN apt install -y libpython3.7-dev
