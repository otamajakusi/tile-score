FROM ubuntu:18.04

RUN dpkg --add-architecture i386
RUN apt update
RUN apt install -y build-essential git vim wget unzip openjdk-8-jdk npm
RUN apt install -y libc6:i386 libncurses5:i386 libstdc++6:i386 lib32z1 libbz2-1.0:i386
RUN npm install -g npm@latest
RUN hash -d npm
RUN npm install -g serverless
COPY android-studio-ide-201.6953283-linux.tar.gz /tmp
RUN tar zxf /tmp/android-studio-ide-201.6953283-linux.tar.gz -C /usr/local
