# Docker - Telegram QA with arXiv papers

## Pre-requisites
If you don't have Docker/Docker-Compose check **Setup Docker** section

<details>
<summary><b>Setup Docker</b></summary>
<p>
## Docker
MacOS: <a href="https://docs.docker.com/docker-for-mac/install/"> https://docs.docker.com/docker-for-mac/install/ </a>
Linux: <a href="https://docs.docker.com/install/linux/docker-ce/ubuntu/"> https://docs.docker.com/install/linux/docker-ce/ubuntu/ </a>

## Docker Compose
Linux: <a href="https://docs.docker.com/compose/install/"> https://docs.docker.com/compose/install/ </a>
</p>
</details>

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
