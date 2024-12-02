## Installation

```
cd /path/to/ScriptKidAgent/agentlib
pip install -e .
cd /path/to/ScriptKidAgent
pip install -e .
```

You should ensure that there is metasploit and nmap are in the host machine.
The more pre-installed tools are in the host, the better performance scriptkid can achieve (just like a real scriptkid)!
For example, curl and searchsploit are recommended.

## Usage

```
scriptkid --ip_segment [ip_segment]
```

for example,

```
scriptkid --ip_segment 127.0.0.1
```

## Test metasploitable2&3 for example

### setup scriptkid docker

```shell
docker build -t scriptkid:latest .

docker run --name scrikptkid \
-it --rm \
--pull never --privileged \
--network pentest \
--env-file=.env \
--entrypoint /bin/bash \
scriptkid:latest
```

### setup metasploitable 2&3

- metasploitable2

```shell
# create docker network for metasploitable2
docker network create --subnet=172.19.0.0/16 --gateway=172.19.0.1 scriptkid 
docker pull tleemcjr/metasploitable2
docker run --network=pentest --ip 172.19.0.2 -h victim -d --rm --name metasploitable2 tleemcjr/metasploitable2
#docker run --network=pentest --ip 172.19.0.3 -h victim3 -d --rm --name metasploitable3 heywoodlh/vulnerable
```

- metasploitable3

```shell
# metasploitable3 with vagrant
cd metasploitable3-workspace
vagrant up

# check ip
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' metasploitable2
```

### evaluate scriptkid

You can use the ip to replace the ip_segment

```shell
scriptkid --ip_segment 172.19.0.0/24
```

### unittest

#### test_execute_command_success

```shell
# in metasploitable
# run ifconfig to get the ip address
# use the ip address to replace the ip
```

Then run

```shell
python -m unittest discover tests
```