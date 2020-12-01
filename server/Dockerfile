FROM ubuntu:18.04

RUN apt update
RUN apt install -y git vim npm wget
RUN npm i -g npm@latest
RUN hash -d npm
RUN npm -v
RUN npm i -g n
RUN n stable
RUN hash -d node
RUN node -v
RUN git clone git@github.com:otamajakusi/tile-score
RUN cd tile-score/server
RUN npm i
