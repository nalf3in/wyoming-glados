FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

WORKDIR /usr/src

RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        python3 \
        python3-pip \
        git \
    \
    && rm -rf /var/lib/apt/lists/* \
    \
    && pip3 install --no-cache-dir -U \
        setuptools \
        wheel \
    \
    && git clone --recurse-submodules https://github.com/nalf3in/wyoming-glados \
    \
    && cd wyoming-glados \
    \
    && python3 download.py \
    \
    && pip install -r requirements.txt

WORKDIR /
COPY run.sh ./

EXPOSE 10201

ENTRYPOINT ["bash", "/run.sh"]