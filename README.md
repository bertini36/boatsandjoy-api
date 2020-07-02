![Heroku](https://heroku-badge.herokuapp.com/?app=heroku-badge)

# Boats & Joy

Source code of [Boats & Joy](https://www.boatsandjoy.com/),
an application to rent boats in Mallorca.
Written in Python, using Django framework, deployed with Heroku and 
development environment managed with Docker-compose.

## Project structure

- Backend: [Django](https://www.djangoproject.com/)
- Frontend: [Vue](https://vuejs.org/)
- Architecture deploy: [Terraform](https://www.terraform.io/)

## Download code

```bash
git clone https://github.com/bertini36/boatsandjoy
```

## Build production environment

### Prerequisites

If you don’t have Terraform installed, download it for your OS from: 

- https://www.terraform.io/downloads.html

If you don't have an Heroku account, create it:

- https://www.heroku.com

and follow the instructions to install its client from:

- https://devcenter.heroku.com/articles/heroku-cli

### Configure access to Heroku

```bash
export APP_NAME=boatsandjoy
heroku authorizations:create --description $APP_NAME
export HEROKU_API_KEY=<TOKEN> HEROKU_EMAIL=<EMAIL>
```

### Build environment

```bash
cd environments/prod/
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

## Build develop environment

### Prerequisites

If you don’t have Docker installed, follow the instructions for your OS:

- On Mac OS X, you’ll need [Docker for Mac](https://docs.docker.com/docker-for-mac/)
- On Windows, you’ll need [Docker for Windows](https://docs.docker.com/docker-for-windows/)
- On Linux, you’ll need [docker-engine](https://docs.docker.com/engine/installation/)

And aditionally install [Docker compose](https://docs.docker.com/compose/install/)

### Set project environ variables

```
cp .env-sample .env
```
Set environment variables defined at `.env`

### Build environment

**Build environment**
```bash
make build
```

**Create database tables**
```bash
make migrate
```

**Collect statics**
```bash
make collectstatic
```

**Create admin user**
```bash
make createsuperuser
```

<p align="center">&mdash; Built with :heart: from Mallorca &mdash;</p>

