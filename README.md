# ![Enisa logo](/graphs/logo-enisa.png?raw=true) exercises 2017

**Table of Contents**

1. [Requirements](#requirements)
2. [Install Dependencies](#install-dependencies)
3. [Installation](#installation)
4. [Training Preparation](#training-preparation)
5. [Troubleshooting](#troubleshooting)



# Requirements

- Any of popular Linux distribution
- 4 GB free RAM
- Dual Core CPU
- 15 GB free space



# Install Dependencies

### Ubuntu 16.04 / Debian 9


```
# apt-get install docker docker-compose curl python-bs4
```
#### WPScan installation
Proceed with installation manual:
https://github.com/wpscanteam/wpscan#manual-install

# Installation

### System preparation

Make sure dockerd is running:

```
# systemctl status docker
```
Add user to docker system group:
```
# usermod -a -G docker <user>
```
Relogin

### Pull images from docker hub
```
$ cd trainings-2017
$ docker-compose pull
```


# Training preparation
### Add environment domains into /etc/hosts
```
# cat etc/hosts >> /etc/hosts
```

### Depends on starting point, run following script:

Day 1 trainings:
```
$ ./build_databases_feed_mgmt.sh
```

Day 2 trainings:
```
$ ./build_databases_investigation.sh
```


# Troubleshooting

### Error while putting up containers with docker-compose
If you see an Error like:
```
Cannot start service misp: b'error creating overlay mount
```
Stop and remove all active containers:
```
docker-compose down
```
Start once agian all containers:
```
docker-compose up
```
