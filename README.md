[![Heroku](http://heroku-badges.herokuapp.com/?app=heroku-badges)](http://heroku-badges.herokuapp.com/projects.html)
[![Requirements Status](https://requires.io/github/bertini36/boatsandjoy-api/requirements.svg?branch=master)](https://requires.io/github/bertini36/boatsandjoy-api/requirements/?branch=master)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

<h3 align="center">
    bertini36/boatsandjoy-api 🛥️
</h3>
<p align="center">
  <a href="#-environment-setup" target="_blank">
    Installation
  </a>&nbsp;&nbsp;•&nbsp;
  <a href="https://github.com/bertini36/boatsandjoy-api/blob/master/Makefile" target="_blank">
    Commands
  </a>
</p>
<p align="center">
A simple availability engine to <a href="https://www.boatsandjoy.com/">rent boats in Mallorca</a>
</p>
<p align="center">
Powered by <a href="https://www.djangoproject.com//" target="_blank">#django</a> and
<a href="https://www.heroku.com/" target="_blank">#heroku</a>
</p>

## ⚙️ Environment Setup

### 🐳 Required tools

1. [Install Docker and Docker Compose](https://www.docker.com/get-started)
2. Clone this project: `git clone https://github.com/bertini36/boatsandjoy-api`
3. Move to the project folder: `boatsandjoy-api`
4. Configure some environment variables: `cp .env-sample .env`

### 🔥 Application execution

1. Install all the dependencies and bring up the project with Docker executing: `make build`
2. Create the database: `make migrate`
3. Create a super user: `make createsuperuser`
4. Run the server: `make up` (by default Django runs applications at 80 port)

## 🚀 Deploy

Automatically deployed when commit at `master` in [Heroku](https://www.heroku.com)

### 🔓 Configure Heroku

First install [Heroku cli](https://devcenter.heroku.com/articles/heroku-cli) 
in your machine. Then login with your credentials

```bash
heroku login
```

Create a superuser to access `admin/`
```bash
heroku run -a boatsandjoy-api "python manage.py createsuperuser"
```

<p align="center">&mdash; Built with :heart: from Mallorca &mdash;</p>

