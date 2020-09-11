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

### Import arXiv metadata
First of all, you need to import the arXiv dataset. For doing so, you'll have to execute the following command:

```sh
$ docker-compose run arxiv-meta
```

### Start the server
For starting the flask server and the telegram bot, please execute:
```sh
$ docker-compose up arxiv-qa
```
