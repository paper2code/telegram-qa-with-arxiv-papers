# Docker - Telegram QA with arXiv papers

## Pre-requisites
If you don't have Docker/Docker-Compose check **Setup Docker** section

<details>
<summary><b>Setup Docker</b></summary>
<p>
<h3>Docker</h3>
MacOS:&nbsp;<a href="https://docs.docker.com/docker-for-mac/install/">https://docs.docker.com/docker-for-mac/install/</a><br />
Linux:&nbsp;<a href="https://docs.docker.com/install/linux/docker-ce/ubuntu/">https://docs.docker.com/install/linux/docker-ce/ubuntu/</a><br />
<hr />
<h3>Docker Compose</h3>
Linux:&nbsp;<a href="https://docs.docker.com/compose/install/">https://docs.docker.com/compose/install/</a><br />
<br />
</p>
</details>

### Docker-Compose with Nvidia support
There is a hack for making your gpu(s) available with docker-compose, for doing so, you will have to add the following to your /etc/docker/daemon.json file:
```json
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
```

## Quick start

### Clone the repository
```sh
git clone --depth=1 https://github.com/paper2code/telegram-qa-with-arxiv-papers
cd telegram-qa-with-arxiv-papers
```

### Update the environment variables
```sh
mv .env-example .env
vim .env
```
- Modify the `TELEGRAM_API` variable with your api key.
- Modify the `SERVER_PORT` variable to whatever you want/need (default: 5018)

### Import arXiv metadata
```
$ docker-compose run arxiv-meta
```

### Start the server and telegram bot
For starting the flask server and the telegram bot, depending on your favourite mode, please execute:

#### CPU mode
```sh
$ docker-compose build arxiv-qa
$ docker-compose up -d elasticsearch  # start elasticsearch server
$ docker-compose run arxiv-train      # train the ArXiV-QA model (will take ~20-30minutes)
$ docker-compose up -d arxiv-qa       # run the server
$ docker-compose up -d arxiv-tg       # run the telegram bot
```

#### GPU mode
```sh
$ docker-compose -f docker-compose.gpu.yml build arxiv-qa    
$ docker-compose -f docker-compose.gpu.yml up -d elasticsearch  # start elasticsearch server
$ docker-compose -f docker-compose.gpu.yml run arxiv-train      # train the ArXiV-QA model (will take ~20-30minutes)
$ docker-compose -f docker-compose.gpu.yml up -d arxiv-qa       # run the server
$ docker-compose -f docker-compose.gpu.yml up -d arxiv-tg       # run the telegram bot
```
