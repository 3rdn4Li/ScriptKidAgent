FROM cybench/kali-linux-large:latest

COPY packages.list /tmp/packages.list

# Install common tools, Python 3.12, and Docker
RUN apt-get update && \
    apt-get install -f && \
    xargs -a /tmp/packages.list apt-get install -y --no-install-recommends && \
    wget https://www.python.org/ftp/python/3.12.7/Python-3.12.7.tgz && \
    tar xzf Python-3.12.7.tgz && \
    cd Python-3.12.7 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.12.7 Python-3.12.7.tgz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

WORKDIR /app

RUN ln -sf /usr/local/bin/python3.12 /usr/bin/python3 && \
    ln -sf /usr/local/bin/pip3.12 /usr/bin/pip3 && \
    python3.12 -m venv /venv

ENV PATH="/venv/bin:$PATH"

COPY agentlib /app/agentlib
COPY scriptkidagent /app/scriptkidagent
COPY pyproject.toml /app/
COPY README.md /app/
RUN /venv/bin/pip install wheel
RUN cd /app/agentlib && /venv/bin/pip install .
RUN cd /app && /venv/bin/pip install -e .


#ENTRYPOINT ["/usr/local/bin/dockerd-entrypoint.sh", "python3", "run_task.py"]
