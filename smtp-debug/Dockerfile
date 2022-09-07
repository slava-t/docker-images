FROM ubuntu:focal

RUN apt-get update && \
    yes | unminimize && \
    apt-get install -qq -y wget python3 python3-pip python3-apt && \
    python3 -m pip install --upgrade pip && \
    apt-get install -qq -y man manpages && \
    apt-get install -qq -y libio-socket-ssl-perl  libdigest-hmac-perl  libterm-readkey-perl libmime-lite-perl libfile-libmagic-perl libio-socket-inet6-perl && \
    apt-get -qq -y install swaks && \
    wget -O /usr/bin/smtp-cli https://raw.githubusercontent.com/mludvig/smtp-cli/00925b88c0ddb6920523783070f4a5e95c666bf6/smtp-cli && \
    chmod +x /usr/bin/smtp-cli && \
    DEBIAN_FRONTEND=noninteractive  TZ=Etc/UTC apt-get install -qq -y \
        tcpdump \
        dnsutils \
        net-tools \
        iputils-ping \
        traceroute \
        iproute2 \
        curl \
        ifupdown \
        iperf3 \
        nmap \
        ssh-client \
        netcat \
        telnet

EXPOSE 25/tcp

CMD python3 -m smtpd -n -c DebuggingServer localhost:25

