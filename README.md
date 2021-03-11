![Heroku](https://heroku-badge.herokuapp.com/?app=heroku-badge)
[![Requirements Status](https://requires.io/github/bertini36/boatsandjoy/requirements.svg?branch=v2)](https://requires.io/github/bertini36/boatsandjoy/requirements/?branch=v2)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

<h3 align="center">
    bertini36/boatsandjoy-api 🛥️
</h3>
<p align="center">
  <a href="#-environment-setup" target="_blank">
    Installation
  </a>&nbsp;&nbsp;•&nbsp;
  <a href="https://github.com/bertini36/boatsandjoy/blob/v2/Makefile" target="_blank">
    Commands
  </a>
</p>
<p align="center">
A simple availability engine to rent boats in Mallorca
</p>
<p align="center">
Powered by <a href="https://www.djangoproject.com//" target="_blank">#django</a> and
<a href="https://www.heroku.com/" target="_blank">#heroku</a>
</p>

## ⚙️ Environment Setup

### 🐳 Required tools

1. [Install Docker and Docker Compose](https://www.docker.com/get-started)
2. Clone this project: `git clone https://github.com/bertini36/boatsandjoy`
3. Move to the project folder: `boatsandjoy`

### 🔥 Application execution

1. Install all the dependencies and bring up the project with Docker executing: `make build`
2. Create the database: `make migrate`
3. Create a super user: `make createsuperuser`
4. Run the server: `make up` (by default Django runs applications at 80 port)
5. You can configure some environment variables: `cp .env-sample .env`

## 🚀 Deploy

### 📝 Prerequisites

If you don’t have Terraform installed, download it for your OS from: 

- https://www.terraform.io/downloads.html

If you don't have an Heroku account, create it:

- https://www.heroku.com

and follow the instructions to install its client from:

- https://devcenter.heroku.com/articles/heroku-cli

### 🔓 Configure access to Heroku

```bash
export APP_NAME=boatsandjoy
heroku authorizations:create --description $APP_NAME
export HEROKU_API_KEY=<TOKEN> HEROKU_EMAIL=<EMAIL>
```

### 🏗️  Build environment

```bash
cd prod/
cp infrastructure.tfsample infrastructure.tf
```

Set environment variables defined at `infrastructure.tf` and then execute terraform

```bash
terraform init
terraform apply
```

If the infrascture has been created correctly in Heroku you will have received project url as output
```
boatsandjoy_url = https://boatsandjoy.herokuapp.com
```

<p align="center">&mdash; Built with :heart: from Mallorca &mdash;</p>

