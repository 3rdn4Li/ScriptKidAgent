## Installation
```
cd /path/to/ScriptKidAgent/agentlib
pip install -e .
cd /path/to/ScriptKidAgent
pip install -e .
```
You should ensure that there is metasploit and nmap are in the host machine.
The more pre-installed tools are in the host, the better performance scriptkid can achieve (just like a real scriptkid)!
For example, curl and exploitdb are recommended.
## Usage
```
scriptkid --ip_segment [ip_segment]
```
for example, 
```
scriptkid --ip_segment 127.0.0.1
```

## In Docker
### Build image
```
docker build -t scriptkid:latest .
```

### Run container
```shell
docker run --name scrikptkid \
-it --rm \
--pull never --privileged \
--network host \
-v "$(pwd)":/app:ro \
--env-file=.env \
--entrypoint /bin/bash \
scriptkid:latest
```