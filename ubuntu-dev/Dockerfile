FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN echo "tzdata tzdata/Areas select America" | debconf-set-selections && \
    echo "tzdata tzdata/Zones/America select Toronto" | debconf-set-selections && \
    apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install -y openssh-client && \
    apt-get install -y apt-transport-https ca-certificates software-properties-common && \
    apt-get install -y build-essential git && \
    apt-get install -y python3 python3-pip python3-venv && \
    apt-get install -y nodejs npm && \
    apt-get install -y htop ncdu tcptrack slurm iftop nmon speedometer bmon sysstat && \
    apt-get install -y dnsutils net-tools iputils-ping traceroute iproute2 curl wget ifupdown iperf3 nmap autossh whois netcat-traditional && \
    apt-get install -y silversearcher-ag ack-grep exuberant-ctags jq && \
    apt-get install -y vim neovim && \
    apt-get install -y npm && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
