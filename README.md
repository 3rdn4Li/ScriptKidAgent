## Installation

```
cd /path/to/ScriptKidAgent/agentlib
pip install -e .
cd /path/to/ScriptKidAgent
pip install -e .
```

You should ensure that there is metasploit, curl and nmap in the host machine.

## Usage

```
scriptkid --ip_segment [ip_segment]
```

for example,

```
scriptkid --ip_segment 127.0.0.1
```

## In Docker

```shell
docker network create pentest
```

### metasploit

```shell
docker build -t scriptkid:latest .

docker run --name scrikptkid \
-it --rm \
--pull never --privileged \
--network pentest \
-v "$(pwd)":/app:ro \
--env-file=.env \
--entrypoint /bin/bash \
scriptkid:latest
```

### metasploitable

```shell
docker pull tleemcjr/metasploitable2
docker run --network=pentest -h victim -it --rm --name metasploitable2 tleemcjr/metasploitable2
```