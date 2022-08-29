FROM ubuntu:focal

ENV PIP_ROOT_USER_ACTION=ignore
COPY ./requirements.txt /tmp/
RUN apt-get update && \
    apt-get install -qq -y python3 python3-pip python3-apt && \
    python3 -m pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt
