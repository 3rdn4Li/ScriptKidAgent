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
--env-file=.env \
--entrypoint /bin/bash \
scriptkid:latest
```

### metasploitable

```shell
docker pull tleemcjr/metasploitable2
docker run --network=pentest -h victim -it --rm --name metasploitable2 tleemcjr/metasploitable2
```

### test

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