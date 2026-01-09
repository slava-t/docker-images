FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_ROOT_USER_ACTION=ignore
COPY ./requirements.txt /tmp/
RUN apt-get update && \
    apt-get install -qq -y less lsb-release vim wget openssh-client sshpass \
    bats python3 python3-pip python3-apt python3-venv && \
    python3 -m venv '/opt/pymain' && \
    /opt/pymain/bin/python3 -m pip install --upgrade pip && \
    /opt/pymain/bin/pip3 install -r /tmp/requirements.txt && \
    ln -s /opt/pymain/bin/ansible /usr/local/bin/ansible && \
    ln -s /opt/pymain/bin/ansible-playbook /usr/local/bin/ansible-playbook && \
    ln -s /opt/pymain/bin/fab /usr/local/bin/fab && \
    rm -f /tmp/requirements.txt
COPY ./fabloom /fabloom
RUN cd /fabloom && /opt/pymain/bin/pip install -e ./
